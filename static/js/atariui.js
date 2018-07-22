COLORS = ["red", "green", "blue", "white", "magenta", "yellow", "cyan",  "black", "orange"];

function atari() {
    onCartridgeChanged = function() {
        console.log("cartridgeChanged");
        cartridge_fn = $("#cartridge-select").val();
        if (atari.postUI) {
            atari.setCartridge(cartridge_fn);
        }
    }

    setCartridge = function(value) {
        $.ajax({url: "/atari/loadCartridge?filename=" + value});
    }

    initButtons = function() {
    }

    updateCartridgeComboBox = function(catridge, cartridges) {
        html = "";

        for (k in cartridges) {
           cartridge_filename = cartridges[k][0];
           cartridge_name = cartridges[k][1];
           selected="";

           if (cartridge_name == cartridge) {
               selected = " selected";
           } else {
               selected = "";
           }

           html = html + "<option value=" + cartridge_filename + selected + ">" + cartridge_name + "</option>";
        }

        $("#cartridge-select").html(html);

        if (atari.didChosen) {
            $("#cartridge-select").trigger("chosen:updated");
        } else {
            $("#cartridge-select").chosen({disable_search: true});
            atari.didChosen = true;
        }
    }

    parseSettings = function(settings) {
        //console.log(settings);
        this.postUI = false;
        try {
            if (settings["cartridge"]) {
                this.lastCartridgeName = settings["cartridge"];
                this.showedCartridgeComboBox=true;
                this.updateCartridgeComboBox(settings["cartridge"], settings["cartridges"])
            }
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

var scale = window.outerWidth / 450;
$('head').append('<meta name="viewport" content="width=450, initial-scale=' + scale + ', maximum-scale=' + scale + ', user-scalable=0">');

$(document).ready(function(){
    atari = atari()
    atari.start();
});

