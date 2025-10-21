window.fusionTools = Object.assign({}, window.fusionTools, {
    featureAnnotation: {
        removeMarker: function(e, ctx) {
                e.target.removeLayer(e.layer._leaflet_id);
                ctx.data.features.splice(ctx.data.features.indexOf(e.layer.feature), 1);
            }

            ,
        tooltipMarker: function(feature, layer, ctx) {
            layer.bindTooltip("Double-click to remove")
        },
        markerRender: function(feature, latlng, context) {
            marker = L.marker(latlng, {
                title: "FeatureAnnotation Marker",
                alt: "FeatureAnnotation Marker",
                riseOnHover: true,
                draggable: false,
            });

            const map = context?.map || window.mainSlideMap;

            if (map) {
                // Smoothly pan and zoom to the marker location, 
                // if you want, you can play around with the zoom levels. For now, it's 7 for our requirements.
                map.flyTo(latlng, 7);  
            }

            return marker;
        }

    }
});