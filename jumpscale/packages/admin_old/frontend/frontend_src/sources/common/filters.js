export function createFilterOptions(obj) {
    // returns a new object as {id: value}, used as data table filter options
    // obj: can be an array or a mapping object

    if (obj instanceof Array) {
        return obj.map((value, index) => {
            return { id: index, value: value }
        });
    } else {
        // assume it's just a mapping otherwise
        return Object.keys(obj).map(key => {
            return { id: key, value: obj[key] }
        });
    }


}
