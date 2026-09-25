"""
Prompt templates with named placeholders, kept separate from the code
that uses them.

Inputs:
    Template files in the "templates" folder next to this file, one per
    prompt, named "<name>.txt". Each file holds a "[system]" section
    and/or a "[user]" section of prompt text with named placeholders
    such as {context} or {question}. Lines starting with "#" before the
    first section are comments. A literal brace is written "{{" or "}}".
    Callers pass the values for the placeholders at render time.

Outputs:
    render_prompt() returns a ready-to-send list of chat messages with
    every placeholder filled in; render_text() returns one filled-in
    section as a string; format_context() turns retrieved chunks into
    the text for a {context} placeholder. Rendering fails with a
    TemplateError naming the problem if a value is missing, an unknown
    value is supplied, or the template file is malformed.

Prompt wording lives only in the template files, so it can change
without editing any application code.
"""

import hashlib
import os
import string

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
SECTION_ROLES = ("system", "user")


class TemplateError(ValueError):
    """Raised when a template cannot be loaded or rendered."""


def template_path(name):
    """
    Locate a template file by name.

    Args:
        name (str): Template name, without the ".txt" extension.

    Returns:
        str: The path to the template file.

    Raises:
        TemplateError: If the name contains a path separator or no such
            template exists.
    """
    if os.path.basename(name) != name or not name:
        raise TemplateError("invalid template name {!r}".format(name))
    path = os.path.join(TEMPLATE_DIR, name + ".txt")
    if not os.path.isfile(path):
        raise TemplateError("no template named {!r} in {}".format(name, TEMPLATE_DIR))
    return path


def load_template(name):
    """
    Read a template file and split it into its sections.

    Args:
        name (str): Template name, without the ".txt" extension.

    Returns:
        dict: "name" (str), "sections" (dict mapping "system"/"user" to
            the section's text, in file order), "placeholders" (list[str],
            every placeholder name used, sorted), and "fingerprint" (str,
            a short hash of the file contents, useful for confirming that
            two callers used the same template).

    Raises:
        TemplateError: If the file has no sections, text appears before
            the first section, a section is repeated or unknown, or a
            placeholder is malformed.
    """
    with open(template_path(name), "r", encoding="utf-8") as handle:
        raw = handle.read()

    sections = {}
    current = None
    for line_number, line in enumerate(raw.splitlines(), start=1):
        header = line.strip()
        if header.startswith("[") and header.endswith("]") and header[1:-1] in SECTION_ROLES:
            current = header[1:-1]
            if current in sections:
                raise TemplateError("{}: section [{}] appears twice".format(name, current))
            sections[current] = []
        elif current is None:
            if header and not header.startswith("#"):
                raise TemplateError("{} line {}: text before the first section".format(name, line_number))
        else:
            sections[current].append(line)

    if not sections:
        raise TemplateError("{}: no [system] or [user] section".format(name))

    texts = {role: "\n".join(lines).strip("\n") for role, lines in sections.items()}
    placeholders = set()
    for role, text in texts.items():
        try:
            for _literal, field, _spec, _conversion in string.Formatter().parse(text):
                if field is not None:
                    if not field.isidentifier():
                        raise TemplateError("{} [{}]: placeholder {{{}}} is not a plain name".format(name, role, field))
                    placeholders.add(field)
        except ValueError as error:
            raise TemplateError("{} [{}]: {}".format(name, role, error))

    return {
        "name": name,
        "sections": texts,
        "placeholders": sorted(placeholders),
        "fingerprint": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12],
    }


def check_values(template, values):
    """
    Confirm the supplied values match a template's placeholders exactly.

    Args:
        template (dict): A template as returned by load_template.
        values (dict): Placeholder name to value.

    Returns:
        None

    Raises:
        TemplateError: If any placeholder has no value, or a value is
            supplied for a name the template does not use (usually a
            typo that would otherwise go unnoticed).
    """
    missing = sorted(set(template["placeholders"]) - set(values))
    unknown = sorted(set(values) - set(template["placeholders"]))
    problems = []
    if missing:
        problems.append("missing value(s) for {}".format(", ".join("{" + name + "}" for name in missing)))
    if unknown:
        problems.append("unknown placeholder(s) {}".format(", ".join(unknown)))
    if problems:
        raise TemplateError("{}: {}".format(template["name"], "; ".join(problems)))


def render_prompt(name, /, **values):
    """
    Fill in a template and return ready-to-send chat messages.

    Args:
        name (str): Template name, without the ".txt" extension.
            Positional-only, so a template may itself use a {name}
            placeholder.
        **values: One keyword argument per placeholder; each value is
            converted with str().

    Returns:
        list[dict]: One message per section in the template, each with
            "role" and "content", in file order.

    Raises:
        TemplateError: If the template cannot be loaded or the values do
            not match its placeholders.
    """
    template = load_template(name)
    check_values(template, values)
    return [
        {"role": role, "content": text.format(**values)}
        for role, text in template["sections"].items()
    ]


def render_text(name, values, section="user"):
    """
    Fill in one section of a template and return it as text.

    Args:
        name (str): Template name, without the ".txt" extension.
        values (dict): Placeholder name to value for that section. Passed
            as a dict rather than keywords so placeholder names can never
            collide with this function's own arguments.
        section (str): "system" or "user".

    Returns:
        str: The filled-in section.

    Raises:
        TemplateError: If the template or section cannot be found, or the
            values do not match the section's placeholders.
    """
    template = load_template(name)
    if section not in template["sections"]:
        raise TemplateError("{}: no [{}] section".format(name, section))
    text = template["sections"][section]
    fields = {field for _l, field, _s, _c in string.Formatter().parse(text) if field is not None}
    check_values({"name": "{} [{}]".format(name, section), "placeholders": sorted(fields)}, values)
    return text.format(**values)


def preview_messages(messages, indent="  | "):
    """
    Format rendered messages for display.

    Args:
        messages (list[dict]): Messages as returned by render_prompt.
        indent (str): Prefix for every displayed line.

    Returns:
        str: Each message's role as a header followed by its content,
            every line prefixed with indent.
    """
    lines = []
    for message in messages:
        lines.append("{}[{}]".format(indent, message["role"]))
        lines.extend(indent + line for line in message["content"].splitlines())
    return "\n".join(lines)


def format_context(chunks, chunk_template="context_chunk"):
    """
    Turn retrieved chunks into the text for a {context} placeholder.

    Args:
        chunks (list[dict]): Chunks with "chunk_id", "section" (str or
            None), and "text" keys.
        chunk_template (str): Template used for each chunk.

    Returns:
        str: Every chunk rendered with chunk_template, separated by a
            blank line.
    """
    return "\n\n".join(
        render_text(chunk_template, {
            "chunk_id": chunk["chunk_id"],
            "section": chunk["section"] or "none",
            "text": chunk["text"],
        })
        for chunk in chunks
    )
