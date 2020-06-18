$(document).ready(function()
{
    elFinder.prototype.i18.en.messages['cmdping'] = 'Ping';
    elFinder.prototype._options.commands.push('ping');
    elFinder.prototype.commands.ping = function()
    {
        // Add command shortcuts
        // this.shortcuts = [{
        //     pattern     : 'ctrl+t'
        // }];

        // return 0 to enable command, -1 to disable
        this.getstate = function(sel) {
            return 0;
        }

        // execute the command business itself
        this.exec = function(hashes) {
            $.each(this.files(hashes), function(i, file) {
                // here you have refs to files
            });
            $.ajax({
                url: "/restmachine/system/master/ping"
            })
                .done(function( data ) {
                alert(data);
            });
            return;
        }
    }

    CodeMirror.commands.autocomplete = function(cm) {
        CodeMirror.showHint(cm, CodeMirror.hint.python);
    };

    var options=
    {
        defaultView : 'list',
        url : '/elfinder/${{config.dockey}}',
        height : {{config.height}},
        width : {{config.width}},
        transport : new elFinderSupportVer1(),
        {{config.commands}}
        commandsOptions: {
            edit : {
            editors : [{
                mimes : ['text/plain', 'text/html', 'text/javascript', 'text/x-python', 'text/x-php', 'text/css', 'text/rtf', 'text/x-ruby', 'text/x-shellscript', 'application/msword'],
                load : function(textarea) {
                    this.myCodeMirror = CodeMirror.fromTextArea(textarea, {
                        lineNumbers: true,
                        theme: "elegant",
                        mode: "python",
                        indentUnit: 4,
                        extraKeys: {"Ctrl-Space": "autocomplete"},

                        onCursorActivity: function() {
                            editor1.addLineClass(hlLine, null, null);
                            hlLine = editor1.addLineClass(editor1.getCursor().line, null, "activeline");
                    }});
                    this.myCodeMirror.setSize(790, 600);
                },
                close : function(textarea, instance) {
                    this.myCodeMirror = null;
                },
                save : function(textarea, editor) {
                    textarea.value = this.myCodeMirror.getValue();
                    this.myCodeMirror = null;
                }
                } ]
            }
        },
        ui :[{{config.tree}}'path', 'stat'],

        getFileCallback : function(files, fm) {
                return false;
        },

        handlers :
        {
            // extract archive files on upload
            dblclick : function(event, elfinderInstance) {
                event.preventDefault();
                elfinderInstance.exec('getfile')
                    .done(function() { elfinderInstance.exec('download'); })
                    .fail(function() { elfinderInstance.exec('open'); });
            },
            upload : function(event, instance)
            {
                var uploadedFiles = event.data.added;
                var archives = ['application/zip', 'application/x-gzip', 'application/x-tar', 'application/x-bzip2'];
                for (i in uploadedFiles)
                {
                    var file = uploadedFiles[i];
                    if (jQuery.inArray(file.mime, archives) >= 0)
                    {
                    instance.exec('extract', file.hash);
                    }
                }
            }
        },
        contextmenu :
        {
            // navbarfolder menu
            //navbar : ['open', '|', 'copy', 'cut', 'paste', 'duplicate', '|', 'rm'],

            // current directory menu
            cwd    : [{{config.dircmd}}],

            // current directory file menu
            files  : [
                {{config.filecmd}}
            ]
        },
        ui: ['toolbar'],
        uiOptions :
        {
            toolbar : [
                ['back', 'forward'],
                ['reload', 'download'],
                ['home', 'up']
            ],
            tree :
            {
                // expand current root on init
                openRootOnLoad : true,
                // auto load current dir parents
                //syncTree : true
            },
            // navbar options
            navbar : {
                minWidth : 100,
                maxWidth : 100
            },
        },
    }
    $('#elfinder{{nr}}').elfinder(options);
});
