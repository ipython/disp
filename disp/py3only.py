from html import escape
from typing import List
import typing
from IPython.display import HTML, DisplayObject

text_formatter = get_ipython().display_formatter.formatters['text/plain']

from there import print


try:
    from IPython.display import get_repr_mimebundle
except ImportError:

    # poor man's version don't protect against recursion
    get_repr_mimebundle =  get_ipython().display_formatter.format 


def repr(o):
    return get_repr_mimebundle(o, include='text/plain').data.get('text/plain')

thecss = """
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

summary > pre {
    display: inline
}


ul.jupyter-flat-container-repr summary {
    margin-left: 0em;
    display: inline-block;
}


details[open] {
    /*display: inline-block;*/
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

details[open] ~ .xx {
    display: block;
}

details ~ .xx {
    display: inline;
}
.output_subarea > ul.jupyter-flat-container-repr, .output_subarea > ul.jupyter-flat-container-repr > p {
    margin-left: 1em;
}
"""

def safe(obj):
    if isinstance(obj, HTML):
        return obj
    else:
        return HTML(escaped_str_or_html(obj))
    

def escaped_str_or_html(obj)-> str:
    """
    Return a string which is safe to embed in html. 
    
    ie, if obj define rerp_html, return this, otherwise escape its text_repr
    """
    return get_repr_mimebundle(obj).data.get('text/html', None) or escape(get_repr_mimebundle(obj).data.get('text/plain', ''))


# we won't register containers (for now), as we need to inject CSS on the page,
# and we don't want o inject it on all the sub-reprs.
# htmlf.for_type(list , lambda t:html_flat_container(t, delims='[]', empty='[]'     ))
# htmlf.for_type(tuple, lambda t:html_flat_container(t, delims='()', empty='()'     ))
# htmlf.for_type(set  , lambda t:html_flat_container(t, delims='{}', empty='set({})'))

def html_flat_container(whatever:List, delims, empty) -> str:
    """
    retrun an Html representation of a list with recursive HTML repr for all sub objects. 
    
    If an object does not define an html representation, fallback on plain-text.
    
    TODO: Fallback on pretty ?
    """
    if not whatever:
        return empty
    x = []
    for index, elem in enumerate(whatever):
        last = (index == len(whatever)-1)
        rpr = escaped_str_or_html(elem)
        pc = '<span class="post-comma">,</span>' if not last else ''
        pl = '<br/>' if last else ''
        x.append('<li>{}{}</li>'.format(rpr, pc))
    return f"""<ul class="jupyter-flat-container-repr">
                    <details open>
                        <summary>{delims[0]}</summary>
                        {''.join(x)}
                    </details>
                    <span class='xx'></span><p>{delims[1]}</p>
                </ul>

            """ 

# htmlf.for_type(list , lambda t:html_flat_container(t, delims='[]', empty='[]'     ))
# htmlf.for_type(tuple, lambda t:html_flat_container(t, delims='()', empty='()'     ))
# htmlf.for_type(set  , lambda t:html_flat_container(t, delims='{}', empty='set({})'))

html_formatter_for_list  = lambda t:html_flat_container(t, delims='[]', empty='[]'     )
html_formatter_for_tuple = lambda t:html_flat_container(t, delims='()', empty='()'     )
html_formatter_for_set   = lambda t:html_flat_container(t, delims='{}', empty='set({})')


def _inner_html_formatter_for_mapping(whatever):
    x = []
    for key,elem in whatever.items():
        mimebundle = get_repr_mimebundle(elem).data
        rpr = mimebundle.get('text/html', mimebundle.get('text/html', None)) or escape(repr(elem))
        x.append(f"""<dl class='jupyter-inner-mapping-repr'>
                        <dt><b>{escape(str(key))}:</b></dt>
                        <dd>{rpr}</dd>
                    </dl>
                  """)
    return ''.join(x)
        

def html_formatter_for_mapping(whatever, *, open=True):
    if not whatever :
        return 'dict({})'
    delims = '{}'
    op = 'open' if open else ''
    return f"""
                <details {op}>
                    <summary>{delims[0]}</summary>
                    {_inner_html_formatter_for_mapping(whatever)}
                </details>
                {delims[1]}
            """

html_formatter_for_dict = html_formatter_for_mapping

# Same thing we don't register dict, but we'll use the code in here
# htmlf.for_type(dict, html_dict)


def html_formatter_for_Response(req):
    import json
    attrs = None
    def in_f(k,v):
        if k == 'headers':
            return HTML(html_formatter_for_mapping(v, open=False))
        else:
            return v

    attrs = _inner_html_formatter_for_mapping({k:in_f(k,v) for (k,v) in vars(req).items() if not k.startswith('_')})
    try:
        json_content = req.json()

        return f"""
            <style>
                {thecss}
            </style>
            <details><summary><pre>{escape(repr(req))}</pre></summary>
                {attrs}
                 <details class="disp-requests-repr">
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
            <details><summary><pre>{escape(repr(req))}</pre></summary>
                {attrs}
            </details>
                """


def details(summary, details_):
    if details:
        rsum = safe(summary)._repr_html_()
        rdetails = safe(details_)._repr_html_()
        return HTML(f"<details><summary>{rsum}</summary>{rdetails}</details>")
    else:
        rsum = escaped_str_or_html(summary)
        return HTML(f"{rsum}")
    
def pre(string):
    assert isinstance(string, str)
    return HTML(f"<pre>{escape(string)}</pre>")

def well(s):
    s = safe(s)._repr_html_()
    return HTML('<div class="well">'+s+'</div>')

def gen_help(obj):
    doc = next(filter(None, (x.__doc__ for x in type(obj).mro())))
    return f"""
    <pre title='{escape(doc)}'>{escape(repr(obj))}<pre>
    """

def general_repr(obj):
    return f'<details><summary><pre>{escape(repr(obj))}<pre></summary>'+\
        _inner_html_formatter_for_mapping({k:v for (k,v) in vars(obj).items() if not k.startswith('_')}) +'</details>'

def ellide(s):
    return s if (len(s) < 75) else s[0:50]+'...'+s[-16:]

def _print_bytestr(arg, p, cycle):
    p.text('<bytes '+ellide(repr(arg))+' at {}>'.format(hex(id(arg))))       

    text_formatter.for_type(bytes, _print_bytestr)

    


def html_formatter_for_type(obj):
    try:
        mro = obj.mro() #[o for o in  if o is not object]
    except TypeError:
        mro = ()
    if len(mro) > 1:
        mime = get_repr_mimebundle(mro[1], include='text/html').data
        return f'<details><summary><pre>{escape(repr(obj))}</pre></summary>'\
                + well(HTML(f"""
                <p><pre alpha>{obj.__doc__ or ''}</pre></p>
                <p> Inherit from :</p>
                <ul>
                  <li>{mime.get('text/html')}</li>
                </ul>"""))._repr_html_()\
                +'</details>'
    else:
        return f'<style>{thecss}</style>'+f'<pre>{escape(repr(obj))}</pre>'
    


def html_formatter_for_builtin_function_or_method(obj):
    ip = get_ipython()
    res = {k:v for (k,v) in ip.inspector.info(obj).items() if v}
    docstring = res.get('docstring')
    res.pop('found')
    res.pop('string_form')
    res.pop('base_class')
    if res.get('definition', None):
        res['definition'] = pre(obj.__name__ + res['definition'])
    if docstring != '<no docstring>':
        res['docstring'] = pre(docstring)
    else:
        del res['docstring']
    #return repr(details(repr(obj), escaped_str_or_html(res)))
    return f'<style>{thecss}</style>'+escaped_str_or_html(details(HTML(escape(repr(obj))), HTML('<div class="well">'+_inner_html_formatter_for_mapping(res)+'<div>')))

    
def html_formatter_for_module(obj):
    return f'<style>{thecss}</style>' + details(HTML(escape(repr(obj))), well(pre(obj.__doc__ or '')))._repr_html_()
