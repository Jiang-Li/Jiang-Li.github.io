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

    d3.json("us-states.json", function(d) {
        console.log("hello")
        return d
        //Bind data and create one path per GeoJSON feature
        // svg.selectAll("path")
        //    .data(json.features)
        //    .enter()
        //    .append("path")
        //    .attr("d", path);
    
    }).then(function (json) {
        console.log("hello")
        svg.selectAll("path")
           .data(json.features)
           .enter()
           .append("path")
           .attr("d", path);

    }).catch(function (error) {
        console.log(error);
      });
  
