## @package gmapcatcher.inputValidation
# Validation of all the user input.

## Validate the text on all the "input" widgets
def allow_only_numbers(entry, text, length, position, max, isInt=True):
    # generate what the new text will be
    text = text[:length]
    pos = entry.get_position()
    old = entry.get_text()
    new_text = old[:pos] + text + old[pos:]

    # Allow the minus as the first char
    if new_text == "-":
        return
    # Allow a maximum number of chars
    elif (len(new_text) > max):
        entry.stop_emission('insert-text')
    else:
        # If an exception is raised the text is not good
        try:
            if isInt:
                int(new_text)
            else:
                float(new_text)
        except Exception:
            entry.stop_emission('insert-text')
