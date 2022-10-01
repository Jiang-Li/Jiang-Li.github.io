    // define the dimensions and margins for the line chart
    // Use the same Margin Convention from HW1 Q3: https://poloclub.github.io/cse6242-2022spring-online/hw1/8rEHLaYmr9 _margin_convention.pdf to layout your graph
    var margin = {top: 50, right: 75, bottom: 50, left: 75}
    var width = 960 - margin.left - margin.right, 
        height = 500 - margin.top - margin.bottom
    

    // define the dimensions and margins for the bar chart


    // define var and functions
    var colorArray = d3.schemeCategory10
    var parseDate = d3.timeParse("%Y");

    // Fetch the data
	var pathToCsv = "average-rating.csv";
    var parseDate = d3.timeParse("%Y");


    d3.dsv(",", pathToCsv, function (d) {
      return {
        // format data attributes if required
            name: d.name,
            year: parseDate(d.year),
            average_rating: Math.floor(+d.average_rating),
            users_rated: +d.users_rated
            }
    }).then(function (data) {
    
    // console.log(data); // you should see the data in your browser's developer tools console

    // append svg element to the body of the page
    // set dimensions and position of the svg element
    let svg = d3
        .select("body")
        .append("svg")
        .attr("id", "line_chart")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("id", "container")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    /* Create line plot using data from csv */

    //Line Chart Data: grouping the data by year and average_rating
    var grouped_games = d3.nest()
        .key(d => d.year)
        .key(d => d.average_rating).sortKeys(d3.ascending)
        .rollup(function(v) {return {count: v.length, year: v[0].year}})
        .entries(data)
        .map(function (obj) {
            for (let i=0; i<10; i++) {
                if (!obj.values.map(x => +x.key).includes(i)) {
                    obj.values.push({ key: i.toString(), value: {count: 0, year: obj.key} })
                }
            }
            obj.values.sort(function(x, y){
                return d3.ascending(x.key, y.key);
             })
            return obj;
        });
    
    // filter year
    grouped_games = grouped_games.filter(function(d) {
        return d.key.includes("2015") || d.key.includes("2016") || d.key.includes("2017")
        || d.key.includes("2018") || d.key.includes("2019")
    })
    // console.log(grouped_games)

    // Bar Chart Data.
    sorted_games = data
        .filter(function(d) {
            return d.year.toString().includes("2015") 
                || d.year.toString().includes("2016") 
                || d.year.toString().includes("2017")
                || d.year.toString().includes("2018") 
                || d.year.toString().includes("2019")
        })
        .sort((a, b) => d3.ascending(a.year, b.year) 
        || d3.descending(a.users_rated, b.users_rated))
     
    var max_count = 0
    grouped_games.forEach(function(element) {
        element.values.forEach(function(d){
            if(max_count < d.value.count) max_count = d.value.count
          }    
        )
    });
  
    // Defining x and y scales
    var xScale = d3.scaleLinear()
    	.range([0,width])
        .domain([0, d3.max(data, function(d){
            return d.average_rating;})]
        );        

    var yScale = d3.scaleLinear()
        .domain([0, max_count])
        .range([height, 0])

    // line chart
    svg.append("g")
        .attr("id", "lines")
        .selectAll()
        .data(grouped_games)
        .enter()
        .append("path")
        .attr("d", function(d){
            return d3.line()
                .x(function(d){return xScale(d.key);}) // this d is under d.values
                .y(function(d){return yScale(d.value.count);})
            (d.values); // this is the input of d3.line()!!!!
        })
        .attr("fill", "none")
        .attr("stroke",function(d, i){ return colorArray[i]});
    
    // To generate dummy values for non-existing data points in part a, it will be helpful 
    // to initialize the array with zeros for each year and then increment the value as you 
    // loop through the data. 
    
    
    // axis X and Y
    var xAxis = d3.axisBottom(xScale)    
    svg.append("g")
        .attr("id", "x-axis-lines")
        .attr("class", "axis")
        .attr("transform", "translate(0,"+height+")")
        .call(xAxis)
        .append("text")
        .attr("class", "axis_label")
        .attr("x", width/2)
        .attr("y", 40)
        .text("Rating")
     

    var yAxis = d3.axisLeft(yScale);
    svg.append("g")
        .attr("id", "y-axis-lines")
        .attr("class", "axis")
        .call(yAxis)
        .append("text")
        .attr("class", "axis_label")
        .attr("y",-50)
        .attr("dy", "0.75em")
        .attr("transform", "rotate(-90)")
        .attr("x", -height/2)
        .text("Count")
     
    // filled circle
    svg.append("g")
        .attr("id", "circles")
        .selectAll()
        .data(grouped_games)
        .enter()
        .append("g")
        .selectAll()
        .data(function(d){return d.values;})
        .enter()
        .append("circle")
        .attr("r",3)
        .attr("cx",function(d){return xScale(d.key)})
        .attr("cy",function(d){return yScale(d.value.count)})
        .attr("fill",function(d, i){ 
            if(d.value.year.toString().includes("2015")) {return colorArray[0]}
            else if (d.value.year.toString().includes("2016")) {return colorArray[1]}
            else if (d.value.year.toString().includes("2017")) {return colorArray[2]}
            else if (d.value.year.toString().includes("2018")) {return colorArray[3]}
            else if (d.value.year.toString().includes("2019")) {return colorArray[4]}
        })
        .on("mouseover",mouseOver)
        .on("mouseout",mouseOut);
    
    // Title
    svg.append("text")
        .attr("id", "line_chart_title")
        .attr("y", -25)
        .attr("x", width/3)
        .text("Board games by Rating 2015-2019")
      

    // ledgend
    var legendBox = svg.append("g")
        .attr("id", "legend")
        .attr("transform", "translate(750,150)");

    var legendEntries = legendBox.selectAll("g")
        .data(grouped_games)
        .enter()
        .append("g")
        .attr("transform", function(d,i) {return "translate(10,"+i*20+")"});

    legendEntries.append("circle")
        .attr("r", 5)
        .attr("fill", function(d, i){return colorArray[i]})

    legendEntries.append("text")
        .attr("x", 15)
        .attr("y",7)
        .text(function(d){return d.key.toString().slice(11,15);})
        .attr("fill", function(d, i){return colorArray[i]})


    /* ------------- Create bar plot using data from csv ---------------------*/

    d3.select("body")
    .append("div")

    //Instantiating the SVG for the bar chart
	let bar_svg = d3
        .select("body")
	    .append("svg")
        .attr("id", "bar_chart")
        // .attr("class","barSVG")
        // .attr("hidden",null)
	    .attr("width", width+margin.left+margin.right)
	    .attr("height", height+margin.top+margin.bottom)
        .append("g")
        .attr("id", "container_2")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    //Controlling mouse over reaction (creating bars)
    function mouseOver(){
        d3.select(this)
            .classed("mouseover",true)
            .attr("r", 6);
        // console.log("Mouse Over!");

        var data = this.__data__;
        // console.log(data)

        function selected_point(d) {
            return {
                rating: +d.key, 
                year: d.value.year.toString().slice(11,15), 
                count: data.value.count}
        }  
        var selection = selected_point(data);
        // console.log(selection)

        bar_data = sorted_games
        .filter(function(d) {
            return d.year.toString().includes(selection.year) 
                && d.average_rating == selection.rating
        })
        .slice(0, 5)
        .map(function(d){
            return{
                name: d.name.slice(0,10),
                year: d.year.toString().slice(11,15),
                rating: +d.average_rating,
                users_rated: +d.users_rated
            }
        })
        .sort((a, b) => d3.descending(a.users_rated, b.users_rated))
        // console.log(bar_data)
 
        if(selection.count > 0 ){
            bar_svg.style("display","block")
        }
        else {
            bar_svg.style("display","none")
        }

        // Title
        bar_svg.append("text")
            .attr("id", "bar_chart_title")
            // .attr("hidden",null)
            .attr("x", width/3)
            .attr("y", -10)
            .text("Top 5 Most Rated Games of "+ selection.year + " with Rating " + selection.rating)


        //Scale
        
        var bar_xScale = d3.scaleLinear()
            .range([0, width-100])
            .domain([0, d3.max(bar_data, function(d){return d.users_rated})]);
        var bar_yScale = d3.scaleBand()
            .range([0, height])
            .domain(bar_data.map(function(d){return d.name;}));

        
        //bar
        var bars = bar_svg
            .append("g")
            .attr("id", "bars")
            .selectAll(".bar")
            .attr("hidden",null)
            .data(bar_data);            
        bars.exit()
            .remove();

        bars.enter()
            .append("rect")
            .merge(bars)
            .attr("class","bar")
            .attr("x",0)
            .attr("height", function(d){
                return bar_yScale.bandwidth();})
            .attr("transform","translate(80,0)")
            .attr("y", function(d){return bar_yScale(d.name);})
            .attr("width", function(d){return bar_xScale(d.users_rated);})
            .attr("fill","steelblue")
            .attr("stroke","white")
            .attr("stroke-width",0.8);

        // Axis
        bar_svg.append("g")
            .attr("id", "x-axis-bars")
            .attr("class", "xAxis")
            .attr("transform", "translate(80,"+height+")");
        bar_svg.select(".xAxis")
            .call(d3.axisBottom(bar_xScale)
            .tickSizeInner([-height]))
            .append("text")
            .attr("x", width/3)
            .attr("y", 30)
            .text("Number of users")        

        bar_svg.append("g")
            .attr("id", "y-axis-bars")
            .attr("class","yAxis")
            .attr("transform","translate(80,0)");
        bar_svg.select(".yAxis")
            .style("font-size","10px")
            .call(d3.axisLeft(bar_yScale))
            .append("text")
            .attr("class", "axis_label")
            .attr("id", "bar_y_axis_label")
            .attr("y",-100)
            .attr("dy", "0.75em")
            .attr("transform", "rotate(-90)")
            .attr("x", -height/2)
            .text("Games")
        
            
    
        

    }

    //Controlling mouse out reaction (removing bar_svg)
    function mouseOut(){
        d3.select(this)
            .classed("mouseover", false)
            .attr("r", 3);
        bar_svg.style("display", "none");
        // svg.select(".barSVG").attr("hidden",true) 
        d3.select(".bar").attr("hidden",true)
        d3.select("#bar_chart_title").remove()   
        d3.select("#x-axis-bars").remove()   
        d3.select("#y-axis-bars").remove()   
        d3.select("#bars").remove()   
    }

        

    }).catch(function (error) {
      console.log(error);
    });

