function AssertException(message) { this.message = message; }
AssertException.prototype.toString = function () {
  return 'AssertException: ' + this.message;
}
 
function assert(exp, message) {
  if (!exp) {
    throw new AssertException(message);
  }
}

// Assume labels are numbered correctly (as we don't care about them, really); just look at the inputs
function returnIndex(node) {
    var inputs = node.getElementsByTagName("input")    
    var id_pattern = new RegExp("^id_(\\d+)-")
    var name_pattern = new RegExp("^(\\d+)-")    
    var i, id, name, id_num, name_num, fieldset_num = -1, result 
    
    for (i = 0; i < inputs.length; i += 1) {
        id = inputs[i].getAttribute("id")
        name = inputs[i].getAttribute("name")
        result = id_pattern.exec(id)
        assert(result, "No ID found in input element")
        id_num = result[1]
        result = name_pattern.exec(name)
        assert(result, "No name found in input element")
        name_num = result[1]
        assert((id_num === name_num), "Name and ID numbers don't match")
        if (fieldset_num === -1) {
            fieldset_num = id_num
        }                                   
        assert( (fieldset_num === id_num), "Fieldset contains inconsistent id numbers " + fieldset_num + " " + id_num)
    }
    return fieldset_num
 }
 
 function resetIndex(node, new_index) {
    var id_pattern = new RegExp("^id_(\\d+)-")
    var name_pattern = new RegExp("^(\\d+)-")    
    var i, id, name, _for, elem
    
    // Fix up inputs
    var inputs = node.getElementsByTagName("input")    
    for (i = 0; i < inputs.length; i += 1) {
        elem = inputs[i]
        id = elem.getAttribute("id")
        name = elem.getAttribute("name")
        id = id.replace(id_pattern, "id_" + new_index + "-")
        name = name.replace(name_pattern, new_index + "-")
        elem.setAttribute("id", id)
        elem.setAttribute("name", name)
        elem.value = ''
    }
    
    // Fix up labels
    var labels = node.getElementsByTagName("label")    
    for (i = 0; i < labels.length; i += 1) {
        elem = labels[i]
        _for = elem.getAttribute("for")
        // for has same pattern as id
        _for = _for.replace(id_pattern, "id_" + new_index + "-")        
        elem.setAttribute("for", _for)        
    }    
 }
 
function addFieldset(area, limit) 
{
    // Get highest index and last element in the input set  
    if(!document.getElementById) return; //Prevent older browsers from getting any further.
    var fieldsets = document.getElementsByClassName(area + "_input_wrapper"); //Get all the input fields in the given area.
    count = fieldsets.length
    var last_fieldset = fieldsets[count-1]
    
    if (fieldsets.length == limit - 1) {
        var button = document.getElementById("more_" + area + "_button")
        button.disabled = true
        button.value = "No more"
    }
    
    // Walk fieldsets to find the highest index inside. We do this in case the fieldset elements get jumbled on the
    // page (due to programming errro) and the last one in the array isn't the one with the highest index.
    var i, result, max_count = 0
    for (i = 0; i < fieldsets.length; i += 1) {
        result = returnIndex(fieldsets[i])  
        if (result > max_count) {
            max_count = result 
        }
    }
    
    // Clone last element and reset id, name, and 'for' elements to highest index + 1 
    var new_fieldset = last_fieldset.cloneNode(true)
    resetIndex(new_fieldset, parseInt(max_count) + 1)
    
    // Insert
    var parent = last_fieldset.parentNode    
    parent.insertBefore(new_fieldset, last_fieldset.nextSibling) // insertAfter, essentially
}

