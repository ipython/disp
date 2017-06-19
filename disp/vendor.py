
try:
    from IPython.core import DataMetadata, RecursiveObject, ReprGetter, get_repr_mimebundle
except ImportError:
    from collections import namedtuple

    class RecursiveObject:
        """
        Default recursive object that provides a recursion repr if needed.

        You may register a formatter for this object that will be call when
        recursion is reached.
        """

        def __init__(self, already_seen):
            self.seen = already_seen
            pass

        def __repr__(self):
            return '<recursion ... {}>'.format(str(self.seen))

        def _repr_html_(self):
            import html
            return '&lt;recursion ... {}&gt;'.format(html.escape(str(self.seen)))



    DataMetadata = namedtuple('DataMetadata', ('data','metadata'))


    class ReprGetter:
        """
        Object to carry recursion state when computing formating information when
        computing rich representation.

        useful when computing representation concurrently of nested object that may
        refer to common resources.
        """

        __slots__ = ('_objs',)

        def __init__(self):
            self._objs = set()

        def get_repr_mimebundle(self, obj, include=None, exclude=None, *, on_recursion=RecursiveObject):
            """
            return the representations of an object and associated metadata.

            An given object can have many representation available, that can be defined
            in many ways: `_repr_*_` methods, `_repr_mimebundle_`, or user-registered
            formatter for types.

            When given an object, :any:`get_repr_mimebundle` will search for the
            various formatting option with their associated priority and return the
            requested representation and associated metadata.


            Parameters
            ----------
            obj : an objects
                The Python objects to get the representation data.
            include : list, tuple or set, optional
                A list of format type strings (MIME types) to include in the
                format data dict. If this is set *only* the format types included
                in this list will be computed.
            exclude : list, tuple or set, optional
                A list of format type strings (MIME types) to exclude in the format
                data dict. If this is set all format types will be computed,
                except for those included in this argument.
            on_recursion: callable
                Return an object to compute the representation when recursion is
                detected.


            Returns
            -------
            (data, metadata) : named tuple of two dicts

                - 0/.data: See :any:`DisplayFormatter.format`.
                - 1/.metadata: See :any:`DisplayFormatter.format`

            Note
            ----

            When :any:`get_repr_mimebundle` detect it is recursively called, it will
            attempt to return the representation of :class:`RecursiveObject`. You
            may register extra formatter for :class:`RecursiveObject`.

            If you are computing objects representation in a concurrent way (thread,
            coroutines, ...), you should make sure to instanciate a
            :class:`ReprGetter` object and use one per task to avoid race conditions.

            If a specific mimetype formatter need to call `get_repr_mimebundle()`
            for another mimeformat, then it must pass the mimetypes values it desire
            to `include` in order to correctly avoid recursion  

            See Also
            --------
                :func:`display`, :any:`DisplayFormatter.format`

            """
            from IPython.core.interactiveshell import InteractiveShell
            if isinstance(include, str):
                include = (include,)
            if not include:
                keys = {(id(obj), None)}
            else:
                keys = {(id(obj), f) for f in include}
            fmt = InteractiveShell.instance().display_formatter.format
            if id(obj) == id(object):
                return DataMetadata({'text/plain':"<class 'object'>"}, {})
            if self._objs.intersection(keys):
                return DataMetadata(*fmt(on_recursion(obj), include=include, exclude=exclude))
            else:
                try:
                    self._objs.update(keys)
                    return DataMetadata(*fmt(obj, include=include, exclude=exclude))
                finally:
                    self._objs.difference_update(keys)

    # Expose this for convenience at the top level. Similar to what the random
    # module in python does. If you want to avoid weird behavior from concurrency:
    #   Instantiate your own.
    get_repr_mimebundle = ReprGetter().get_repr_mimebundle
