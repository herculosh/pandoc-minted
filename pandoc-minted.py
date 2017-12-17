#!/usr/bin/env python
''' A pandoc filter that has the LaTeX writer use minted for typesetting code.

Usage:
    pandoc --filter ./minted.py -o myfile.tex myfile.md
'''

from string import Template
from pandocfilters import toJSONFilter, RawBlock, RawInline
import pandocfilters as pf


def unpack_code(value, language):
    ''' Unpack the body and language of a pandoc code element.

    Args:
        value       contents of pandoc object
        language    default language
    '''
    [[_, classes, attributes], contents] = value

    if len(classes) > 0:
        language = classes[0]

    attributes = ', '.join('='.join(x) for x in attributes)

    return {'contents': contents, 'language': language,
            'attributes': attributes}


def unpack_metadata(meta):
    ''' Unpack the metadata to get pandoc-minted settings.

    Args:
        meta    document metadata
    '''
    settings = meta.get('pandoc-minted', {})
    if settings.get('t', '') == 'MetaMap':
        settings = settings['c']

        # Get language.
        language = settings.get('language', {})
        if language.get('t', '') == 'MetaInlines':
            language = language['c'][0]['c']
        else:
            language = None

        return {'language': language}

    else:
        # Return default settings.
        return {'language': 'text'}


def latex(s):
    return pf.RawBlock('latex', s)


def minted(key, value, format, meta):
    ''' Use minted for code in LaTeX.

    Args:
        key     type of pandoc object
        value   contents of pandoc object
        format  target output format
        meta    document metadata
    '''

    # required, beamer wont work.
    if format != 'latex':
        return

    # https://git.framasoft.org/Gwendal/better-pandoc-markdown2beamer/blob/master/columnfilter.py
    if key == "Para":
        value = pf.stringify(value)
        if value.startswith('[') and value.endswith(']') and \
                'columns' in value:
            content = value[1:-1]
            if content == "columns":
                return latex(r'\begin{columns}')
            elif content == "/columns":
                return latex(r'\end{columns}')
            elif content.startswith("column="):
                return latex(r'\column{%s\textwidth}' % content[7:])
        if value.startswith('[') and value.endswith(']') and \
                'questions' in value:
            content = value[1:-1]
            if content == "questions":
                return latex(r'\begin{questions}')
            elif content == "/questions":
                return latex(r'\end{questions}')
            elif content.startswith("question="):
                return latex(r'\asdfasdquestion\[%s\]' % content[9:])
        if value.startswith('[') and value.endswith(']') and \
                'parts' in value:
            content = value[1:-1]
            if content == "parts":
                return latex(r'\begin{parts}')
            elif content == "/parts":
                return latex(r'\end{parts}')
        if value.startswith('[') and value.endswith(']') and \
                'sol' in value:
            content = value[1:-1]
            if content == "sol":
                return latex(r'\begin{solutionorlines}[1in]')
            elif content == "/sol":
                return latex(r'\end{solutionorlines}')
            elif content.startswith("sol="):
                return latex(r'\begin{solutionorlines}[%s]' % content[4:])
        if value.startswith('[') and value.endswith(']') and \
                'question' in value:
            content = value[1:-1]
            if content == "question":
                return latex(r"\question")
            elif content.startswith("question="):
                return latex(r'\question[%s]' % content[9:])
        if value.startswith('[') and value.endswith(']') and \
                'part' in value:
            content = value[1:-1]
            if content == "part":
                return latex(r"\part")
            elif content.startswith("part="):
                return latex(r'\part[%s]' % content[5:])
        if value.startswith('[') and value.endswith(']') and \
                'hideinpublic' in value:
            content = value[1:-1]
            if content == "hideinpublic":
                return latex(r"\ifshowforanswer%")
            elif content == "/hideinpublic":
                return latex(r'\fi')
    # Determine what kind of code object this is.
    if key == 'CodeBlock':
        template = Template(
            '\\begin{minted}[$attributes,breaklines,autogobble]{$language}\n$contents\n\end{minted}'
        )
        Element = RawBlock
    elif key == 'Code':
        template = Template('\\mintinline[$attributes]{$language}{$contents}')
        Element = RawInline
    else:
        return

    settings = unpack_metadata(meta)

    code = unpack_code(value, settings['language'])

    return [Element(format, template.substitute(code))]


if __name__ == '__main__':
    toJSONFilter(minted)
