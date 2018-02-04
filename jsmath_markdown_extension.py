import markdown

from markdown.util import etree
from markdown.util import AtomicString


class JsMathPattern(markdown.inlinepatterns.Pattern):
    """Inline markdown processing of math."""

    def __init__(self, tag, pattern):
        super(JsMathPattern, self).__init__(pattern)
        self.math_tag_class = 'math'
        self.tag = tag

    def handleMatch(self, m):
        node = markdown.util.etree.Element(self.tag)
        node.set('class', self.math_tag_class)

        prefix = '\\(' if m.group('prefix') == '$' else m.group('prefix')
        suffix = '\\)' if m.group('suffix') == '$' else m.group('suffix')
        node.text = markdown.util.AtomicString(prefix + m.group('math') + suffix)

        return node


class JsMathCorrectDisplayMath(markdown.treeprocessors.Treeprocessor):
    """Corrects invalid html that results from a <div> being put inside
    a <p> for displayed math.

    Modified from Pelican's render_math plugin.
    """

    def __init__(self, math_tag_class='math'):
        self.math_tag_class = math_tag_class

    def correct_html(self, root, children, div_math, insert_idx, text):
        """Separates out <div class="math"> from the parent tag <p>. Anything
        in between is put into its own parent tag of <p>"""

        current_idx = 0

        for idx in div_math:
            el = markdown.util.etree.Element('p')
            el.text = text
            el.extend(children[current_idx:idx])

            # Test to ensure that empty <p> is not inserted
            if len(el) != 0 or (el.text and not el.text.isspace()):
               root.insert(insert_idx, el)
               insert_idx += 1

            text = children[idx].tail
            children[idx].tail = None
            root.insert(insert_idx, children[idx])
            insert_idx += 1
            current_idx = idx+1

        el = markdown.util.etree.Element('p')
        el.text = text
        el.extend(children[current_idx:])

        if len(el) != 0 or (el.text and not el.text.isspace()):
            root.insert(insert_idx, el)

    def run(self, root):
        """Searches for <div class="math"> that are children in <p> tags and corrects
        the invalid HTML that results"""

        for parent in root:
            div_math = []
            children = list(parent)

            for div in parent.findall('div'):
                if div.get('class') == self.math_tag_class:
                    div_math.append(children.index(div))

            # Do not process further if no displayed math has been found
            if not div_math:
                continue

            insert_idx = list(root).index(parent)
            self.correct_html(root, children, div_math, insert_idx, parent.text)
            root.remove(parent)  # Parent must be removed last for correct insertion index

        return root


class JsMathExtension(markdown.Extension):
    """A markdown extension enabling math in Markdown."""
    def __init__(self):
        super(JsMathExtension, self).__init__()

    def extendMarkdown(self, md, md_globals):
        inline_regex = r'(?P<prefix>\$)(?P<math>.+?)(?P<suffix>(?<!\s)\2)'
        display_regex = r'(?P<prefix>\$\$|\\begin\{(.+?)\})(?P<math>.+?)(?P<suffix>\2|\\end\{\3\})'

        md.inlinePatterns.add('jsmath_displayed', JsMathPattern('div', display_regex), '<escape')
        md.inlinePatterns.add('jsmath_inlined', JsMathPattern('span', inline_regex), '<escape')

        # Correct the invalid HTML that results from the displayed math (<div> tag within a <p> tag)
        md.treeprocessors.add('jsmath_correctdisplayedmath', JsMathCorrectDisplayMath(), '>inline')
