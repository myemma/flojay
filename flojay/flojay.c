#include <Python.h>
#include <api/yajl_gen.h>
#include <stdio.h>
#include <string.h>

#define DEFAULT_BUFFER_SIZE 4096

typedef enum {seq_type = 1, map_type = 2, gen_type = 3, unknown_type = 0} dfs_stack_type;

struct dfs_stack {
  /*
    a simple linked list structure for
    walking the object graph in a depth first fashion
  */
  PyObject * elt;
  /* Only used for list stack elements to track the location in the list */
  /* Or the position in a map iter */
  Py_ssize_t index;
  Py_ssize_t length;
  struct dfs_stack * parent;
  dfs_stack_type type;
};

typedef struct {
  PyObject_HEAD
  PyObject * default_func;
  int ensure_ascii;
  size_t bufsize;
  PyObject * beautify;
  char * indent_string;
} flojay_JSONEncoderObject;

typedef struct {
  PyObject_HEAD
  struct dfs_stack * head;
  yajl_gen gen;
  flojay_JSONEncoderObject * encoder;
} flojay_generator;

static PyObject *
flojay_generator_new(PyTypeObject * type)
{
  flojay_generator *self = (flojay_generator *)type->tp_alloc(type, 0);
  self->head = PyMem_New(struct dfs_stack, 1);
  self->head->parent = NULL;
  self->head->elt = NULL;
  self->head->index = 0;
  self->head->length = 0;
  self->head->type = unknown_type;
  return (PyObject *) self;
}

static
int _flojay_handle_yajl_error(yajl_gen_status status)
{
  if(status == yajl_gen_status_ok)
    return 0;

  switch(status) {
  case yajl_gen_keys_must_be_strings:
    PyErr_SetString(PyExc_RuntimeError, "At a point where a map key is generated, a function other than yajl_gen_string was called");
    break;
  case yajl_max_depth_exceeded:
    PyErr_SetString(PyExc_RuntimeError, "YAJL's maximum generation depth was exceeded. see YAJL_MAX_DEPTH");
    break;
  case yajl_gen_in_error_state:
    PyErr_SetString(PyExc_RuntimeError, "A generator function (yajl_gen_XXX) was called while in an error state");
    break;
  case yajl_gen_generation_complete:
    PyErr_SetString(PyExc_RuntimeError, "A complete JSON document has been generated");
    break;
  case yajl_gen_invalid_number:
    PyErr_SetString(PyExc_RuntimeError, "yajl_gen_double was passed an invalid floating point value (infinity or NaN)");
    break;
  case yajl_gen_no_buf:
    PyErr_SetString(PyExc_RuntimeError, "A print callback was passed in, so there is no internal buffer to get from");
    break;
  case yajl_gen_invalid_string:
    PyErr_SetString(PyExc_RuntimeError, "returned from yajl_gen_string() when the yajl_gen_validate_utf8 option is enabled and an invalid was passed by client code");
    break;
 default:
   PyErr_Format(PyExc_RuntimeError, "YAJL unknown error: %d", status);
  }
  return -1;
}

static
void _flojay_base_save_to_stack(flojay_generator * self, PyObject * new_elt, dfs_stack_type type)
{
  
  struct dfs_stack * new = PyMem_New(struct dfs_stack, 1);
  Py_INCREF(new_elt);
  new->parent = self->head;
  new->type = type;
  self->head = new;
  self->head->elt = new_elt;
  self->head->index = 0;
  self->head->length = 0;
}

static
void _flojay_save_seq_to_stack(flojay_generator * self, PyObject * seq)
{
  _flojay_base_save_to_stack(self, seq, seq_type);
  self->head->index = 0;
  self->head->length = PySequence_Size(seq);
}

static
void _flojay_save_map_to_stack(flojay_generator * self, PyObject * map)
{
  _flojay_base_save_to_stack(self, map, map_type);
}

static
void _flojay_save_gen_to_stack(flojay_generator * self, PyObject * gen)
{
  _flojay_base_save_to_stack(self, gen, gen_type);
}

static
void _flojay_pop_from_stack(flojay_generator * self)
{
  struct dfs_stack * parent = self->head->parent;
  Py_XDECREF(self->head->elt);
  PyMem_Free((void *) self->head);
  self->head = parent;
}

static void
flojay_generator_dealloc(flojay_generator * self)
{
  while(self->head && self->head->parent) {
    _flojay_pop_from_stack(self);
  }
  yajl_gen_free(self->gen);
  Py_DECREF(self->encoder);
  self->ob_type->tp_free((PyObject*)self);
}

static
int _flojay_encode(flojay_generator * self, PyObject * obj)
{
  char * buf;
  Py_ssize_t len;
  yajl_gen_status status = yajl_gen_status_ok;

  if(obj == Py_None) {
    status = yajl_gen_null(self->gen);
  } else if(obj == Py_True) {
    status = yajl_gen_bool(self->gen, 1);
  } else if(obj == Py_False) {
    status = yajl_gen_bool(self->gen, 0);
  } else if(PyUnicode_Check(obj)) {
    PyObject * str = PyUnicode_AsUTF8String(obj);
    PyString_AsStringAndSize(str, &buf, &len);
    status = yajl_gen_string(self->gen, (const unsigned char *) buf, (size_t) len);
    Py_XDECREF(str);
  } else if(PyString_Check(obj)) {
    PyString_AsStringAndSize(obj, &buf, &len);
    status = yajl_gen_string(self->gen, (const unsigned char *) buf, (size_t) len);
  } else if(PyInt_Check(obj)) {
    status = yajl_gen_integer(self->gen, PyInt_AS_LONG(obj));
  } else if(PyNumber_Check(obj)) {
    PyObject * str = PyObject_Str(obj);
    PyString_AsStringAndSize(str, &buf, &len);
    status = yajl_gen_number(self->gen, (const char *) buf, (size_t) len);
    Py_XDECREF(str);
  } else if(PySequence_Check(obj)) {
    status = yajl_gen_array_open(self->gen);
    _flojay_save_seq_to_stack(self, obj);
  } else if(PyIter_Check(obj)) {
    status = yajl_gen_array_open(self->gen);
    _flojay_save_gen_to_stack(self, obj);
  } else if(PyMapping_Check(obj)) {
    status = yajl_gen_map_open(self->gen);
    _flojay_save_map_to_stack(self, obj);
  } else {
    PyObject * newobj =
      PyObject_CallFunctionObjArgs(self->encoder->default_func, obj, NULL);
    
    if(NULL == (void *) newobj) {
      return -1;
    }
    if (Py_EnterRecursiveCall(" while encoding a JSON object")) {
      Py_DECREF(newobj);
      return -1;
    }
    int return_value = _flojay_encode(self, newobj);
    Py_LeaveRecursiveCall();
    Py_DECREF(newobj);
    return return_value;
  }

  return _flojay_handle_yajl_error(status);
}

static
PyObject * _flojay_next_element(flojay_generator * self)
{
  PyObject * key, * value;

  switch(self->head->type) {
  case seq_type:
    if(self->head->index < self->head->length) {
      PyObject *retval = PySequence_GetItem(self->head->elt, self->head->index);
      self->head->index += 1;
      return retval;
    } else {
      return NULL;
    }
  case map_type:
    if(PyDict_Next(self->head->elt, &self->head->index, &key, &value)) {
      _flojay_encode(self, key);
      Py_INCREF(value);
      return value;
    } else {
      return NULL;
    }
  case gen_type:
    return PyIter_Next(self->head->elt);
  default:
    return Py_None;
  }
}

static int
flojay_generator_init(flojay_generator * self, PyObject * encoder, PyObject * args)
{
  PyObject * obj;
  self->encoder = (flojay_JSONEncoderObject *) encoder;
  self->gen = yajl_gen_alloc(NULL);
  yajl_gen_config(self->gen, yajl_gen_beautify, (self->encoder->beautify == Py_True) ? 1 : 0);
  if(self->encoder->indent_string)
    yajl_gen_config(self->gen, yajl_gen_indent_string, self->encoder->indent_string);
  yajl_gen_config(self->gen, yajl_gen_validate_utf8, 1);
  
  if(!PyArg_ParseTuple(args, "O", &obj))
    return -1;

  yajl_gen_clear(self->gen);

  Py_INCREF(encoder);

  if(-1 == _flojay_encode(self, obj))
    return -1;

  return 0;
}

static PyObject *
flojay_generator_next(flojay_generator * self)
{  
  PyObject * obj;
  char * buf;
  size_t len;
  yajl_gen_status status;

  while(1) {
    if((NULL == self->head) || (self->head->type == unknown_type)) {
      status = yajl_gen_get_buf(self->gen, (const unsigned char **) &buf, &len);
        if(-1 == _flojay_handle_yajl_error(status))
          return NULL;
        if(len == 0)
          return NULL;
        PyObject * str = PyString_FromStringAndSize(buf, (Py_ssize_t) len);
        yajl_gen_clear(self->gen);
        return str;
    }

    obj = _flojay_next_element(self);
    if(NULL == obj) {
      if((self->head->type == seq_type) || (self->head->type == gen_type)) {
        yajl_gen_array_close(self->gen);
      } else if(self->head->type == map_type) {
        yajl_gen_map_close(self->gen);
      }
      _flojay_pop_from_stack(self);
    } else {
      if(-1 == _flojay_encode(self, obj)) {
        Py_DECREF(obj);
        return NULL;
      }
      Py_DECREF(obj);
    }

    status = yajl_gen_get_buf(self->gen, (const unsigned char **) &buf, &len);
    if(-1 == _flojay_handle_yajl_error(status))
      return NULL;
    if(len >= self->encoder->bufsize) {
      PyObject * str = PyString_FromStringAndSize(buf, (Py_ssize_t) len);
      yajl_gen_clear(self->gen);
      return str;
    }
  }
}

PyTypeObject flojay_generator_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "flojay_generator",             /* tp_name */
    sizeof(flojay_generator),       /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)flojay_generator_dealloc, /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    0,                              /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)flojay_generator_next, /* tp_iternext */
    0,                              /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    0,                              /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    flojay_generator_new,           /* tp_new */
};

static PyObject *
flojay_JSONEncoder_default(PyObject * self, PyObject * args)
{
  PyObject * obj;
  if(!PyArg_ParseTuple(args, "O", &obj))
    return NULL;

  PyObject * repr = PyObject_Repr(obj);
  PyErr_Format(PyExc_TypeError, "%s is not JSON serializable", PyString_AsString(repr));

  return NULL;
}

static int
flojay_JSONEncoder_init(PyObject * pyself, PyObject * args, PyObject * kwords)
{
  static char *kwlist[] = {"default", "buffer_size", "beautify", "indent_string", NULL};
  PyObject * default_func = Py_None;
  PyObject * beautify;
  char * indent_string;
  size_t indent_string_size;

  size_t buffer_size = DEFAULT_BUFFER_SIZE;
  flojay_JSONEncoderObject * self = (flojay_JSONEncoderObject *) pyself;

  if(!PyArg_ParseTupleAndKeywords(args, kwords, "|OiOz", kwlist,
                                  &default_func, &buffer_size, &beautify, &indent_string))
    return -1;

  self->bufsize = buffer_size;
  self->beautify = beautify;
  if(indent_string == NULL) {
    self->indent_string = NULL;
  } else {
    indent_string_size = strlen(indent_string);
    self->indent_string = PyMem_New(char, indent_string_size + 1);
    if(!self->indent_string) {
      return -1;
    }
    memcpy(self->indent_string, indent_string, indent_string_size + 1);
  }

  if(default_func && Py_None != default_func) {
    Py_INCREF(default_func);
    self->default_func = default_func;
  } else {
    self->default_func = PyObject_GetAttrString((PyObject *) self, "default");
  }

  return 0;
}

static PyObject *
flojay_JSONEncoder_iterencode(PyObject * self, PyObject * args)
{
  flojay_generator * generator;

  generator = (flojay_generator *) flojay_generator_new(&flojay_generator_type);
  if(-1 == flojay_generator_init(generator, self, args))
    return NULL;
  
  return (PyObject *) generator;
}

static void
flojay_JSONEncoder_dealloc(flojay_JSONEncoderObject * self)
{
  if(NULL != self->indent_string) {
    PyMem_Free(self->indent_string);
  }
  self->ob_type->tp_free((PyObject*)self);
}

static PyMethodDef flojay_JSONEncoder_methods[] = {
  {
    "__init__",
    (PyCFunction)flojay_JSONEncoder_init, METH_VARARGS | METH_KEYWORDS,
    "Init"
  },
  {
    "iterencode",
    (PyCFunction)flojay_JSONEncoder_iterencode, 1,
    "Yield hunks of JSON now and again"
  },
  {
    "default",
    (PyCFunction)flojay_JSONEncoder_default,  1,
    "Default handler for objects of unknown type"
  },
  {NULL}  /* Sentinel */
};

static PyTypeObject flojay_JSONEncoderType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "flojay.JSONEncoder",             /*tp_name*/
    sizeof(flojay_JSONEncoderObject), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    flojay_JSONEncoder_dealloc,/*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "flojay JSON encoder, based on yajl",  /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    flojay_JSONEncoder_methods,  /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    flojay_JSONEncoder_init,   /* tp_init */
    PyType_GenericAlloc,       /* tp_alloc */
    0                          /* tp_new */
};

static PyMethodDef FlojayMethods[] = {
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initflojay(void) 
{
    PyObject* m;

    flojay_JSONEncoderType.tp_new = PyType_GenericNew;
    flojay_generator_type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&flojay_JSONEncoderType) < 0)
        return;
    if (PyType_Ready(&flojay_generator_type) < 0)
        return;


    m = Py_InitModule3("flojay", FlojayMethods,
                       "flojay JSON encoder, using yajl");
    
    Py_INCREF(&flojay_JSONEncoderType);
    Py_INCREF(&flojay_generator_type);
    PyModule_AddObject(m, "JSONEncoder", (PyObject *)&flojay_JSONEncoderType);
}


