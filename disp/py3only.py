"""
This submodule contains formatting utilities and formatters which will work only
on Python 3.6+. There is no inherent reasons why it would not work on earlier
version of Python, it just makes use of features that are 3.6 only – Like
f-strings – to make the code more readable. Feel free to send patches that makes
it compatible with earlier versions of python
"""


from html import escape
from typing import List
from IPython.display import HTML
from .vendor import get_repr_mimebundle


text_formatter = get_ipython().display_formatter.formatters['text/plain']


def repr(o):
    """
    Alternative implementation of repr, whcih goes through IPython display system from plain-text. 

    We go directly though the formatter to avoid recursion complication with
    get_mime_types, ans for a tiny bit more speed.

    If the real repr is needed, then one need to use builtins.repr
    """
    return text_formatter(o)


# This is the CSS we want to inject before each top-level object. We should
# (try-to) make it to work with most frontend, as not all frontends do support
# CSS injection, let's try to not rely on too much customisation


thecss = """

/* summary::-webkit-details-marker {
  display: none;
}

summary {
  text-decoration-line: underline;
  text-decoration-style: dotted;
  
} */

.rendered_html pre, .rendered_html code {
    background-color: transparent; /* bug in notebook css */
}

.rendered_html .jupyter-extra-info ul{
    list-style: none;
}

.jupyter-extra-info {
    background-color: hsla(0, 0%, 5%, 0.07); 
    padding: 0.5em;
    border: thin solid silver;
}
dl.jupyter-inner-mapping-repr {
    padding-left: 1em;
    margin-bottom: 0;
}

dl.jupyter-inner-mapping-repr > dd {
    padding-left:2em;
}

ul.jupyter-flat-container-repr li > p{
    padding-left:2em;
    display: inline;
    padding: 0;
}

ul.jupyter-flat-container-repr, ul.jupyter-flat-container-repr ul , ul.jupyter-flat-container-repr ul il{
    list-style-type: none;   
    display: inline;
    padding-left: 0;
}

ul.jupyter-flat-container-repr > details {
    display: inline-block;
    margin-left: -1em;
}

ul.jupyter-flat-container-repr li{
    padding-left:2em;
    list-style-type: none;
}

summary > code {
    display: inline
}

ul.jupyter-flat-container-repr summary {
    margin-left: 0em;
    display: inline-block;
}

.rendered_html ul.jupyter-flat-container-repr {
    padding-left: 0px;
    margin-left: 0em;
}

.jupyter-flat-container-repr details {
    display: inline;
}

.jupyter-flat-container-repr details ~ p {
    margin-top: 0;
    display: inline;
}

.jupyter-flat-container-repr details[open] ~ p {
    /*display: block;*/
}

details.jupyter-details[open] ~ .jupyter-breaking-placeholder {
    display: block;
}

.jupyter-details ~ .jupyter-breaking-placeholder {
    display: inline;
}
.output_subarea > ul.jupyter-flat-container-repr, .output_subarea > ul.jupyter-flat-container-repr > p {
    margin-left: 1em;
}
"""


##########################################################################
#                    Utilities                                                  #
##########################################################################

def safe(obj):
    """
    Given an object (str, or html), return an HTML version. 

    That is to say, if Object is already an HTML object, return it. If it's a string, escape it. 

    """
    if isinstance(obj, HTML):
        return obj
    else:
        return HTML(htmlify_repr(obj))


def htmlify_repr(obj)-> str:
    """
    Return a string which is safe to embed in html. 

    ie, if obj define rerp_html, return this, otherwise escape its text_repr
    """
    return get_repr_mimebundle(obj).data.get('text/html', None) or\
        escape(repr(obj))


def details(summary, details_):
    if details:
        rsum = safe(summary)._repr_html_()
        rdetails = safe(details_)._repr_html_()
        return HTML(f"<details class='jupyter-details'><summary>{rsum}</summary>{rdetails}</details>")
    else:
        rsum = htmlify_repr(summary)
        return HTML(f"{rsum}")


def code(string):
    assert isinstance(string, str)
    return HTML(f"<code>{escape(string)}</code>")


def well(s):
    s = safe(s)._repr_html_()
    return HTML('<div class="jupyter-extra-info">' + s + '</div>')


##########################################################################
#                           Formatters                                          #
##########################################################################


def html_flat_container(container: List, delims, empty) -> str:
    """Retrun an Html representation of a list with recursive HTML repr for all sub objects. 

    If an object does not define an html representation, fallback on plain-text.

    """
    if not container:
        return empty
    x = []
    for index, elem in enumerate(container):
        last = (index == len(container) - 1)
        rpr = htmlify_repr(elem)
        pc = '<span class="post-comma">,</span>' if not last else ''
        x.append('<li>{}{}</li>'.format(rpr, pc))
    return f"""<ul class="jupyter-flat-container-repr">
                    <details class='jupyter-details' open>
                        <summary>{delims[0]}</summary>
                        {''.join(x)}
                    </details>
                    <span class='jupyter-breaking-placeholder'></span><p>{delims[1]}</p>
                </ul>

            """


def html_formatter_for_list(t):
    return html_flat_container(t, delims='[]', empty='[]')


def html_formatter_for_tuple(t):
    return html_flat_container(t, delims='()', empty='()')


def html_formatter_for_set(t):
    return html_flat_container(t, delims='{}', empty='set({})')


def _inner_html_formatter_for_mapping(mapping):
    x = []
    for key, elem in mapping.items():
        mimebundle = get_repr_mimebundle(elem).data
        representation = mimebundle.get(
            'text/html', mimebundle.get('text/html', None)) or escape(repr(elem))
        x.append(f"""<dl class='jupyter-inner-mapping-repr'>
                        <dt><b>{escape(str(key))}:</b></dt>
                        <dd>{representation}</dd>
                    </dl>
                  """)
    return ''.join(x)


def html_formatter_for_mapping(mapping, *, open=True):
    if not mapping:
        return 'dict({})'
    delims = '{}'
    op = 'open' if open else ''
    return f"""
            <details class='jupyter-details'  {op}>
                <summary>{delims[0]}</summary>
                {_inner_html_formatter_for_mapping(mapping)}
            </details>
            {delims[1]}
            """


html_formatter_for_dict = html_formatter_for_mapping


def html_formatter_for_Response(req):
    import json
    attrs = None

    def in_f(k, v):
        if k == 'headers':
            return HTML(html_formatter_for_mapping(v, open=False))
        else:
            return v

    attrs = _inner_html_formatter_for_mapping(
        {k: in_f(k, v) for (k, v) in vars(req).items() if not k.startswith('_')})
    try:
        json_content = req.json()

        return f"""
            <style>
                {thecss}
            </style>
            <details class='jupyter-details'><summary><code>{escape(repr(req))}</code></summary>
                {attrs}
                 <details class="jupyter-details">
                    <summary>Content (JSON)</summary>
                    {_inner_html_formatter_for_mapping(json_content)}
                 </details>
            </details>
            """

    except json.JSONDecodeError:
        return f"""
            <style>
                {thecss}
            </style>
            <details class='jupyter-details'><summary><code>{escape(repr(req))}</code></summary>
                {attrs}
            </details>
                """


def gen_help(obj):
    doc = next(filter(None, (x.__doc__ for x in type(obj).mro())))
    return f"""
    <code title='{escape(doc)}'>{escape(repr(obj))}<code>
    """


def general_repr(obj):
    return f'<style>{thecss}</style>' +\
           f'<details class="jupyter-details"><summary><code>{escape(repr(obj))}<code></summary>' +\
           _inner_html_formatter_for_mapping({k: v for (k, v) in vars(obj).items() if not k.startswith('_')}) +\
           '</details>'


def html_formatter_for_type(obj):
    try:
        mro = obj.mro()  # [o for o in  if o is not object]
    except TypeError:
        mro = ()
    if len(mro) > 1:
        mime = get_repr_mimebundle(mro[1], include='text/html').data
        return f'<style>{thecss}</style>' + \
            f'<details class="jupyter-details" ><summary><code>{escape(repr(obj))}</code></summary>'\
            + well(HTML(f"""
                <p><code alpha>{obj.__doc__ or ''}</code></p>
                <p> Inherit from :</p>
                <ul>
                  <li>{mime.get('text/html')}</li>
                </ul>"""))._repr_html_()\
            + '</details>'
    else:
        return f'<style>{thecss}</style>' + f'<code>{escape(repr(obj))}</code>'


def html_formatter_for_builtin_function_or_method(obj):
    ip = get_ipython()
    res = {k: v for (k, v) in ip.inspector.info(obj).items() if v}
    docstring = res.get('docstring')
    res.pop('found')
    res.pop('string_form')
    res.pop('base_class')
    if res.get('definition', None):
        res['definition'] = code(obj.__name__ + res['definition'])
    if docstring != '<no docstring>':
        res['docstring'] = code(docstring)
    else:
        del res['docstring']
    return f'<style>{thecss}</style>' + htmlify_repr(details(code(repr(obj)), well(HTML(_inner_html_formatter_for_mapping(res)))))


def html_formatter_for_module(obj):
    return f'<style>{thecss}</style>' + details(code(repr(obj)), well(code(obj.__doc__ or '')))._repr_html_()
