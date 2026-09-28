    // define the dimensions and margins for the line chart
    var margin = {top: 50, right: 75, bottom: 50, left: 75}
    var width = 1024 - margin.left - margin.right, 
        height = 768 - margin.top - margin.bottom    
    var colorArray = d3.schemeCategory10
    var parseDate = d3.timeParse("%Y")
        
    let svg = d3
        .select("body")
        .append("svg")
        .attr("id", "line_chart")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("id", "container")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var path = d3.geoPath()
             .projection(d3.geoAlbersUsa());

    var color = d3.scaleQuantile()
            .range(["rgb(237,248,233)", "rgb(186,228,179)",
             "rgb(116,196,118)", "rgb(49,163,84)", "rgb(0,109,44)"]);

    d3.csv("post_count_state.csv", function(d) {
        return {
            state: d.state, 
            count:+d.count.replace(/,/g, '')
        }
    }).then(function(data) {
        color.domain(data.map(x=>x.count));
        d3.json("us-states.json").then(function(json){
        //Merge the ag. data and GeoJSON
        // Loop through once for each ag. data value
            for (var i = 0; i < data.length; i++) {
    
                //Grab state name
                var dataState = data[i].state;
    
                //Grab data value, and convert from string to float
                var dataValue = data[i].count;
    
                //Find the corresponding state inside the GeoJSON
                for (var j = 0; j < json.features.length; j++) {
    
                var jsonState = json.features[j].properties.name;
    
                if (dataState == jsonState) {
    
                    //Copy the data value into the JSON
                    json.features[j].properties.value = dataValue;
    
                    //Stop looking through the JSON
                    break;
                }
    
                }
            }

            // tip
            var tip = d3.tip().attr("id", "tooltip")
            // .attr('class', 'd3-tip')
            .html(
                function(d) {
                    // if (typeof(d.properties.value) == "undefined") d.properties.value="N/A"
                    return "<text> " +d.properties.name + " <br>"
                    + d.properties.value + " jobs </text> ";
                  }
            );

            svg.call(tip)

            // map
            svg.selectAll("path")
            .data(json.features)
            .enter()
            .append("path")
            .attr("d", path)
            .style("fill", function(d) {
                //Get data value
                var value = d.properties.value;
                // console.log(value)
                if (value) {
                    return color(value);
                } else {
                    //If value is undefined…
                    return "#ccc";
                }
            })
            .on('mouseover', tip.show)
            .on('mouseout', tip.hide)

     
            console.log("hello")
            //legend                     
            svg.append("g")
                .attr("id", "legend")
                .attr("class", "legendQuant")
                .attr("transform", "translate(800,300)");
            
            var legend = d3.legendColor()
                .labelFormat(d3.format(".0f"))
                .useClass(false)
                .titleWidth(100)
                .scale(color);
            
            svg.select(".legendQuant")
                .call(legend);

            
            //title
            svg.append("text")
                .attr("id", "title")
                .attr("y", 0)
                .attr("x", width/3)
                .attr("font-size", "24px")
                .text("Indeed.com Analytics Job Listing Count, 2022-10-02")

            // credit
            svg.append("text")
                .attr("id", "credit")
                .attr("y", height-200)
                .attr("x", width-50)
                .attr("font-size", "12px")
                .text("Dr. Jiang Li")
                .on("click", function() { window.open("https://jiang-li.github.io/"); }); 

        }) // json
    }) // end csv

