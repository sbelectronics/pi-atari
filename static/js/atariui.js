COLORS = ["red", "green", "blue", "white", "magenta", "yellow", "cyan",  "black", "orange"];

function atari() {
    onCartridgeChanged = function() {
        console.log("cartridgeChanged");
        cartridge_fn = $("#cartridge-select").val();
        if (atari.postUI) {
            atari.setCartridge(cartridge_fn);
        }
    }

    onCategoryChanged = function() {
        console.log("categoryChanged");
        category_name = $("#category-select").val();
        if (atari.postUI) {
            atari.updateCartridgeComboBox("", atari.cartridges, category_name)
        }
    }

    onReset = function() {
        if (atari.postUI) {
            atari.reset();
        }
    }

    setCartridge = function(value) {
        $.ajax({url: "/atari/loadCartridge?filename=" + value});
    }

    reset = function() {
        $.ajax({url: "/atari/reset"});
    }

    initButtons = function() {
        $("#reset").click(function() { atari.reset(); });
    }

    updateCartridgeComboBox = function(catridge, cartridges, category_filter) {
        html = "";

        for (k in cartridges) {
           cartridge_filename = cartridges[k][0];
           cartridge_name = cartridges[k][1];
           category_name = cartridges[k][2];

           if (category_name == category_filter) {
               selected="";

               if (cartridge_name == cartridge) {
                   selected = " selected";
               } else {
                   selected = "";
               }

               html = html + "<option value=" + encodeURIComponent(cartridge_filename) + selected + ">" + cartridge_name + "</option>";
           }
        }

        $("#cartridge-select").html(html);

        $("#cartridge-select").css("width", "300px");

        if (atari.didChosen) {
            $("#cartridge-select").trigger("chosen:updated");
        } else {
            $("#cartridge-select").chosen({disable_search: true});
            atari.didChosen = true;
        }
    }

    updateCategoryComboBox = function(categories) {
        html = "";

        for (k in categories) {
           selected="";
           html = html + "<option value=" + encodeURIComponent(categories[k]) + selected + ">" + categories[k] + "</option>";
        }

        $("#category-select").html(html);

        if (atari.didChosenCat) {
            $("#category-select").trigger("chosen:updated");
        } else {
            $("#category-select").chosen({disable_search: true});
            atari.didChosenCat = true;
        }
    }

    parseSettings = function(settings) {
        console.log(settings);
        this.postUI = false;
        try {
            if (settings["cartridge"]) {
                this.lastCartridgeName = settings["cartridge"];
            }

            this.updateCategoryComboBox(settings["categories"]);
            this.cartridges = settings["cartridges"];

            this.updateCartridgeComboBox(settings["cartridge"], settings["cartridges"], settings["categories"][0])
        }
        finally {
            this.postUI = true;
        }
    }

    requestSettings = function() {
        $.ajax({
            url: "/atari/getStatus",
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                atari.parseSettings(newData);
                //setTimeout("atari.requestSettings();", 1000);
            },
            error: function() {
                console.log("error retrieving settings");
                setTimeout("atari.requestSettings();", 5000);
            }
        });
    }

    start = function() {
         this.postUI = true;
         this.initButtons();
         this.requestSettings();
    }

    return this;
}

// autoscale the website to fit on the iphone
var scale = window.outerWidth / 450;
$('head').append('<meta name="viewport" content="width=450, initial-scale=' + scale + ', maximum-scale=' + scale + ', user-scalable=0">');

$(document).ready(function(){
    atari = atari()
    atari.start();
});

