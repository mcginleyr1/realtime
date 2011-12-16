brükva
========

Asynchronous [Redis](http://redis.io/) client that works within [Tornado](http://tornadoweb.org/) IO loop.

Usage
-----

Input:

    import logging
    logging.basicConfig()
    import brukva
    c = brukva.Client()
    c.connect()
    loop = c.connection._stream.io_loop
    def on_result(result):
        print result
    c.set('foo', 'bar', on_result)
    c.get('foo', on_result)
    c.hgetall('foo', [on_result, lambda r: loop.stop()])
    loop.start() # start tornado mainloop

Output:

    True
    bar
    ERROR:brukva.client:ResponseError (on HGETALL [('foo',), {}]): Operation against a key holding the wrong kind of value
    ResponseError (on HGETALL [('foo',), {}]): Operation against a key holding the wrong kind of value

Tips on testing
---------------

Run redis-server on localhost:6379 with option "timeout 1".
Run tests with the following command:

    ./run_nose.sh


Credits
-------
brukva is developed and maintained by [Konstantin Merenkov](mailto:kmerenkov@gmail.com)

 * Inspiration: [redis-py](http://github.com/andymccurdy/redis-py)
 * Third-party software: [adisp](https://code.launchpad.net/adisp)


License
-------
See LICENSE file.
Long story short: WTFPL v2
