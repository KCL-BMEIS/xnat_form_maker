//needs to be at end of form.....
function calcDateDiff(propertyOne,  propertyTwo, property, format) {
    if (document.getElementById(propertyOne) !== null) {
        // the variable is defined
        if ( document.getElementById(propertyTwo) !== null) {
        // the variable is defined
        //  const date1      new Date(2019, 08, 03, 11, 45, 55);
            var dt1 = document.getElementById(propertyOne).value;
            var dt2 = document.getElementById(propertyTwo).value;
            const date1 = new Date(dt1.substring(0,4), dt1.substring(5,7), dt1.substring(8,10), dt1.substring(11,13),dt1.substring(14,16),dt1.substring(17,19));
            const date2 = new Date(dt2.substring(0,4), dt2.substring(5,7), dt2.substring(8,10), dt2.substring(11,13),dt2.substring(14,16),dt2.substring(17,19));
            // end - start returns difference in milliseconds
            const diffTime = Math.abs(date2 - date1);

            // get days
            if (format.includes('d')){
                //day
                document.getElementById(property).value = diffTime/1000/60/60/24;
            }
            else if (format.includes('m')) {
                // minute
                document.getElementById(property).value = diffTime/1000/60;
            }
        }
    }
}

function calcSum(property, things) {
                var sum = 0.0;
                for (let i=0; i<things.length; i++) {
                    var el = things[i];
                    var value = document.getElementById(el).value;
                   if (value) {
                       value = value.replace('+','').replace(' ','')
                       var val = parseFloat(value);
                       val.toFixed(2);
                       sum += +val;
                   }
                }
                document.getElementById(property).value = sum;
}

function updateTime(property,  time) {
            tm = document.getElementById(time).value;
            document.getElementById(property).value =  tm;
          }


