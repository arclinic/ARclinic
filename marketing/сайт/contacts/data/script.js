if (document.getElementById('map2').length !== 0) {
    ymaps.ready(init); 
    var myMap, myMap2, myPlacemark, myPlacemark2;
    
    function init() {
    
        /*myMap = new ymaps.Map("map", {
            center: [59.845479, 30.310529],
            zoom: 14.5
        });*/

        myMap2 = new ymaps.Map("map2", {
            center: [59.915026, 30.324184],
            zoom: 14.85
        }); 
        
        /*var geometry = [
            [59.84924,30.32123],
            [59.84926,30.31864],
            [59.84880,30.31862],
            [59.84878,30.31679],
            [59.84848,30.31681],
            [59.84849,30.31490],
            [59.84772,30.31499],
            [59.84519,30.30999],
            [59.84500,30.31029],
            [59.84515,30.31052]
        ];*/

        var geometry2 = [
            [59.916629,30.318444],
            [59.917102,30.319753],
            [59.914658,30.322330],
            [59.915726,30.326093],
            [59.913739,30.328146],
            [59.913966,30.328869],
            [59.913683,30.329273]
        ];

        properties = {
            hintContent: "Маршрут до клиники"
        },
    
        options = {
            draggable: true,
            strokeColor: '#ff0000',
            strokeWidth: 3
        },
    
        //polyline = new ymaps.Polyline(geometry, properties, options);
        polyline2 = new ymaps.Polyline(geometry2, properties, options);
    
        //myMap.geoObjects.add(polyline);
        myMap2.geoObjects.add(polyline2);
    
        /*myMap.controls.add(
            new ymaps.control.ZoomControl()
        );*/
        myMap2.controls.add(
            new ymaps.control.ZoomControl()
        ); 
    
        /*myPlacemark = new ymaps.Placemark([59.845469, 30.311161], {
            hintContent: 'ARclinic',
            balloonContent: 'ARclinic',
            iconContent: 'ARclinic'
        }, {
            iconLayout: 'default#image',
            iconImageHref: '/local/templates/arclinic/img/map_marker.png',
            iconImageSize: [60, 82],
            iconImageOffset: [-10, -70]
        });*/
        myPlacemark2 = new ymaps.Placemark([59.913726, 30.329181], {
            hintContent: 'ARclinic',
            balloonContent: 'ARclinic',
            iconContent: 'ARclinic'
        }, {
            iconLayout: 'default#image',
            iconImageHref: '/local/templates/arclinic/img/map_marker.png',
            iconImageSize: [60, 82],
            iconImageOffset: [5, -77]
        });
        
        //myMap.geoObjects.add(myPlacemark);
        myMap2.geoObjects.add(myPlacemark2);
    };
}