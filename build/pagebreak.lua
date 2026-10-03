-- Turn each horizontal rule in the memo into a page break.
--
-- The memo's rules already sit exactly where the document should break:
-- after the section 1 prose, after the Part A exhibits, and after the
-- section 2 prose.  Doing it this way keeps memo.md readable as Markdown
-- (no stray \newpage in the source) while making the page limits
-- verifiable in the PDF: section 1's prose is pages 1-2 and nothing else,
-- section 2's prose is one page and nothing else.
function HorizontalRule()
  return pandoc.RawBlock('latex', '\\newpage')
end
