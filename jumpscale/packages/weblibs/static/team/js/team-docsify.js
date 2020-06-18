function TeamWidgetPlugin() {
    return function (hook) {
        hook.ready(() => {
            TeamWidget.setupHandlers();
        });
    }
}
