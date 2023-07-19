(() => {
    'use strict'
  
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation');
  
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
  
        form.classList.add('was-validated');
      }, false);
    })
  })();

function get_events() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_events?season=' + $('#season_selection').val() + '&team_number=' + $('#team_number').val());
    xhr.onreadystatechange = function () {
        $('#event_selection_form').removeClass('d-none');
        $('#event_selection').empty()
        var resp = xhr.response.split('~');
        
        for (var i = 0; i < (resp.length-1)/3; i++) {
            var opt = document.createElement('option');
            opt.value = resp[i*3+2]
            opt.innerHTML = resp[i*3+1]
            $('#event_selection').append(opt);
        }
    }
    xhr.send();
}

function get_rankings() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_rankings?event=' + $('event_selection').val())
}