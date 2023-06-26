        function calcDateDiff(propertyOne,  propertyTqo, property) {
                var start = document.getElementById(propertyOne).value;
                var end = document.getElementById(propertyTwo).value
                // end - start returns difference in milliseconds
                var diff = new Date(end - start);
                // get days
                document.getElementById(property).value = diff/1000/60/60/24;
              }

        function updateTime(property,  time) {
                    tm = document.getElementById(time).value;

                    document.getElementById(property).value =  tm;
                  }