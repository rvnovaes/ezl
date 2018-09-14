from codemirror import CodeMirrorTextarea

code_mirror_schema = CodeMirrorTextarea(
    mode="javascript",
    theme="material",
    config={
        'fixedGutter': True,
        'indentUnit': 4
    }
)