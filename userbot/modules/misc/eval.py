# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import sys
import ast
import contextlib
from os import remove
from io import StringIO

from ..help import add_help_item
from userbot import BOTLOG, BOTLOG_CHATID, bot
from userbot.events import register
from userbot.utils.tgdoc import *


@register(outgoing=True, pattern=r"^\.eval(?:\s+([\S\s]+)|$)")
async def evaluate(e):
    """ For .eval command, evaluates the given Python expression. """
    reply = await e.get_reply_message()
    if e.is_channel and not e.is_group:
        await e.edit("`Eval isn't permitted on channels`")
        return

    if e.pattern_match.group(1):
        expression = e.pattern_match.group(1)
    elif reply:
        expression = reply.message
    else:
        await e.edit(str(Bold("Give an expression to evaluate")))
        return

    head = Section(Bold("Query:"), Code(expression), indent=0)

    try:
        response, out = await async_eval(expression, bot=bot, event=e, reply=reply)
        evaluation = str(response)

        if evaluation:
            if isinstance(evaluation, str):
                if len(evaluation) >= 4096:
                    file = open("output.txt", "w+")
                    file.write(evaluation)
                    file.close()
                    await e.client.send_file(
                        e.chat_id,
                        "output.txt",
                        reply_to=e.id,
                        caption="`Output too large, sending as file`",
                    )
                    remove("output.txt")
                    return

        result = Section(Bold("Result:"), Code(response), indent=0)
        output = Section(Bold("Output:"), Code(out), indent=0)
        section = Section(
            head,
            result if response else None,
            output if out else None,
            indent=0,
            spacing=2
        )

        await e.edit(str(section))

    except Exception as err:
        error = SubSection(Bold("Error:"), Code(str(err)), indent=0)
        section = Section(head, error, indent=0, spacing=2)
        await e.edit(str(section))

    if BOTLOG:
        await e.client.send_message(
            BOTLOG_CHATID,
            f"#EVAL\nEval query ```{expression}``` was executed successfully")


# https://stackoverflow.com/a/57349931/974936
async def async_eval(code, **kwargs):
    # Note to self: please don't set globals here as they will be lost.
    # Don't clutter locals
    locs = {}
    # Restore globals later
    globs = globals().copy()
    # This code saves __name__ and __package into a kwarg passed to the function.
    # It is set before the users code runs to make sure relative imports work
    global_args = "_globs"
    while global_args in globs.keys():
        # Make sure there's no name collision, just keep prepending _s
        global_args = "_" + global_args
    kwargs[global_args] = {}
    for glob in ["__name__", "__package__"]:
        # Copy data to args we are sending
        kwargs[global_args][glob] = globs[glob]

    root = ast.parse(code, 'exec')
    code = root.body
    if isinstance(code[-1], ast.Expr):  # If we can use it as a lambda return (but multiline)
        code[-1] = ast.copy_location(ast.Return(code[-1].value), code[-1])  # Change it to a return statement
    # globals().update(**<global_args>)
    glob_copy = ast.Expr(ast.Call(func=ast.Attribute(value=ast.Call(func=ast.Name(id='globals', ctx=ast.Load()),
                                                                    args=[], keywords=[]),
                                                     attr='update', ctx=ast.Load()),
                                  args=[], keywords=[ast.keyword(arg=None,
                                                                 value=ast.Name(id=global_args, ctx=ast.Load()))]))
    glob_copy.lineno = 0
    glob_copy.col_offset = 0
    ast.fix_missing_locations(glob_copy)
    code.insert(0, glob_copy)
    args = []
    for a in list(map(lambda x: ast.arg(x, None), kwargs.keys())):
        a.lineno = 0
        a.col_offset = 0
        args += [a]
    fun = ast.AsyncFunctionDef('tmp', ast.arguments(args=[], vararg=None, kwonlyargs=args, kwarg=None, defaults=[],
                                                    kw_defaults=[None for i in range(len(args))]), code, [], None)
    fun.lineno = 0
    fun.col_offset = 0
    mod = ast.Module([fun])
    comp = compile(mod, '<string>', 'exec')

    exec(comp, {}, locs)

    with temp_stdio() as out:
        result = await locs["tmp"](**kwargs)
        try:
            globals().clear()
            # Inconsistent state
        finally:
            globals().update(**globs)
        return result, out.getvalue()


# Create a temporary stdio
@contextlib.contextmanager
def temp_stdio(stdout=None, stderr=None):
    old_out = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old_out


add_help_item(
    "eval",
    "Misc",
    "Evaluates a small Python expression using `eval()`.",
    """
    `.eval (expression)`
    
    Or, in response to a message
    `.eval`
    """
)
