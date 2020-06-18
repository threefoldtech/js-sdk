var editor1 = CodeMirror.fromTextArea(document.getElementById("code1"),
{
lineNumbers: $linenr,
readOnly: $readonly,
theme: "monokai",
autoRefresh: "False",
lineWrapping: $wrap,
mode: "python",
onCursorActivity: function() {
    editor1.addLineClass(hlLine, null, null);
    hlLine = editor1.addLineClass(editor1.getCursor().line, null, "activeline");
    }
}
);
var hlLine = editor1.addLineClass(0, "activeline");

function copyText1() {
    var text=editor1.getValue()
    document.hiddenForm1.text.value = text;
    document.forms["hiddenForm1"].submit();
}
