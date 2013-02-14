# flojay 

flojay provides incremental serialization of Python data structures as
JSON documents, and an event-based JSON parser to allow for incremental
deserialization. It can be used to create and process JSON documents
that are larger than working memory.

It is based on [yajl](http://lloyd.github.com/yajl/) version 2, a
copy of which is included in this distribution.

# example

    import flojay
    import sys

    # Produce JSON from a generator, printing partial results
    # as they become available

    encoder = flojay.JSONEncoder()
    json_generator = encoder.iterencode(xrange(100))
    for hunk in json_generator:
        print hunk


    # Read an array of JSON numbers from stdin input,
    # summing the values as they are read


    class ExampleCallbacks(object):
        def __init__(self):
            self.sum = 0

        def handle_start_array(self):
            pass

        def handle_end_array(self):
            pass

        def handle_number(self, value):
            self.sum += value

    callbacks = ExampleCallbacks()

    parser = flojay.JSONEventParser(callbacks)

    while 1:
        row = sys.stdin.readline()
        if len(row) == 0:
            break
        parser.parse(row)
        print "The current total is: %d" % (callbacks.sum,)
    
