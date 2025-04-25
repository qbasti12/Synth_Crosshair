$(document).ready(function() {
    function updateTempSettings() {
        var innerLineWidth = parseFloat($('#innerLineWidth').val());
        var innerLineLength = parseFloat($('#innerLineLength').val());
        var borderWidth = parseFloat($('#borderWidth').val());
        var gap = parseFloat($('#gap').val());
        var innerLineColor = $('#innerLineColor').val();
        var borderColor = $('#borderColor').val();
        var showBorder = $('#showBorder').is(':checked');
        var showInnerLines = $('#showInnerLines').is(':checked');
        var showCenterDot = $('#showCenterDot').is(':checked');
        var centerDotSize = parseFloat($('#centerDotSize').val());
        var centerDotColor = $('#centerDotColor').val();
        var showCenterDotBorder = $('#showCenterDotBorder').is(':checked');
        var centerDotBorderColor = $('#centerDotBorderColor').val();
        var centerDotBorderWidth = parseFloat($('#centerDotBorderWidth').val());
        var scale = parseFloat($('#scale').val());

        $.ajax({
            url: '/update_temp',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                innerLineWidth: innerLineWidth,
                innerLineLength: innerLineLength,
                borderWidth: borderWidth,
                gap: gap,
                innerLineColor: innerLineColor,
                borderColor: borderColor,
                showBorder: showBorder,
                showInnerLines: showInnerLines,
                showCenterDot: showCenterDot,
                centerDotSize: centerDotSize,
                centerDotColor: centerDotColor,
                showCenterDotBorder: showCenterDotBorder,
                centerDotBorderColor: centerDotBorderColor,
                centerDotBorderWidth: centerDotBorderWidth,
                scale: scale
            }),
            success: function(response) {
                // Temporary crosshair settings updated successfully
            },
            error: function(error) {
                alert('Error updating temporary crosshair settings.');
            }
        });
    }

    function syncSliderWithInput(slider, input) {
        $(slider).on('input change', function() {
            $(input).val($(this).val());
            updateTempSettings();
        });

        $(input).on('input change', function() {
            $(slider).val($(this).val());
            updateTempSettings();
        });
    }

    function adjustWindowHeight() {
        var totalHeight = $('#crosshair-form').outerHeight(true);
        $('body').height(totalHeight + 50); // Add some padding
    }

    syncSliderWithInput('#innerLineWidth', '#innerLineWidthValue');
    syncSliderWithInput('#innerLineLength', '#innerLineLengthValue');
    syncSliderWithInput('#borderWidth', '#borderWidthValue');
    syncSliderWithInput('#gap', '#gapValue');
    syncSliderWithInput('#centerDotSize', '#centerDotSizeValue');
    syncSliderWithInput('#centerDotBorderWidth', '#centerDotBorderWidthValue');
    syncSliderWithInput('#scale', '#scaleValue');

    $('#innerLineColor, #borderColor, #centerDotColor, #showBorder, #showInnerLines, #showCenterDot, #showCenterDotBorder, #centerDotBorderColor').on('input change', function() {
        updateTempSettings();
    });

    $('#apply-button').click(function() {
        $.ajax({
            url: '/apply',
            type: 'POST',
            contentType: 'application/json',
            success: function(response) {
                // Crosshair settings applied successfully
            },
            error: function(error) {
                alert('Error applying crosshair settings.');
            }
        });
    });

    $('#reset-button').click(function() {
        $.ajax({
            url: '/reset',
            type: 'POST',
            contentType: 'application/json',
            success: function(response) {
                // Crosshair settings reset successfully
                location.reload(); // Reload the page to reset the form
            },
            error: function(error) {
                alert('Error resetting crosshair settings.');
            }
        });
    });

    $('#scale').on('input change', function() {
        updateTempSettings();
    });

    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
            adjustWindowHeight();
        });
    }

    adjustWindowHeight(); // Initial adjustment
});

let profiles = {};

function addProfile() {
    const profileName = prompt("Profilname eingeben:");
    if (profileName) {
        fetch('/save_profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ profileName })
        }).then(response => response.json())
          .then(data => {
              if (data.success) {
                  profiles[profileName] = { ...temp_crosshair_settings };
                  updateProfileList();
              }
          });
    }
}

function updateProfileList() {
    const profileList = document.getElementById("profile-list");
    profileList.innerHTML = '';
    for (const profileName in profiles) {
        const li = document.createElement("li");
        li.textContent = profileName;

        const loadButton = document.createElement("button");
        loadButton.textContent = "Load";
        loadButton.onclick = () => loadProfile(profileName);

        li.appendChild(loadButton);
        profileList.appendChild(li);
    }
}

function loadProfile(profileName) {
    fetch('/load_profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ profileName })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              temp_crosshair_settings = { ...profiles[profileName] };
              // Hier können Sie die Crosshair-Einstellungen aktualisieren
          }
      });
}

function renameProfile(oldName) {
    const newName = prompt("Neuen Profilnamen eingeben:", oldName);
    if (newName && newName !== oldName) {
        profiles[newName] = profiles[oldName];
        delete profiles[oldName];
        updateProfileList();
    }
}