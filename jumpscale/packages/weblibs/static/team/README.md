# Team

A team widget that include also a docsify plugin.



## Interface


### _TeamWidget.render(dataset, order)_

Render a div with team photos and description popup

* dataset: a list of objects with avatar, full_name and description, e.g {avatar: 'image.png', full_name: "My Name", descirption: '...'}
* order: the order of listing team members (either "rank" or "random")


### _TeamWidget.setupHandlers()_

Setup event handlers to open full description popup when clicking the photos, this should be called after the page is fully loaded and the widget is already rendered.


### _TeamWidget.init()_

Replace every element with class `team-container` with a team widget and setup required handlers, it excpects a `<code>` element with the json data inside that element, like:

```html
<div class="team-container">
    <code>
        {dataset: [...], order: "random"}
    </code>
</div>
```

## Docsify plugin

To use as docsify plugin, you need to use `TeamWidget.render` to replace any custom json (as a code block) by team widget, then you need to setup the event handlers using the simple plugin provided:

```javascript
window.$docsify = {
    markdown: {
        renderer: {
            code: function(code, lang) {
                if (lang === "team") {
                    var data = JSON.parse(code);
                    return TeamWidget.render(data.dataset, data.order);
                }
                return this.origin.code.apply(this, arguments);
            }
        }
    },
    plugins: [
        TeamWidgetPlugin(),
    ]
};
```
