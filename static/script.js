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

var team = 492

async function getChannel() {
    let res = await fetch(`/get_channels?team=${team}`)
    res = await res.text();
     if (res != "No current events") {
        var options = {
            width: 854,
            height: 480,
            channel: res,
        };
        var player = new Twitch.Player("twitch-embed", options);
        player.setVolume(0.5);
    }
}

async function get_events() {
    let res = await fetch(`/get_events?season=${$('#season_selection').val()}&team_number=${$('#team_number').val()} `);
    res = await res.text();

    $('#event_selection_form').removeClass('d-none');
    $('#event_selection').empty()

    var resp = res.split('~');

    for (var i = 0; i < (resp.length - 1) / 3; i++) {
        var opt = document.createElement('option');
        opt.value = resp[i * 3 + 2]
        opt.innerHTML = resp[i * 3 + 1]
        $('#event_selection').append(opt);
    }
}

async function get_rankings() {
    $('#calculate_spinner').removeClass('d-none');
    $('#calculate_label').addClass('d-none');

    var use_OPR = (document.getElementById("use_OPR").checked) ? 'True' : 'False';
    var use_CCWMS = (document.getElementById("use_CCWMS").checked) ? 'True' : 'False';
    var use_overall_EPA = (document.getElementById("use_overall_EPA").checked) ? 'True' : 'False';
    var use_auto_EPA = (document.getElementById("use_auto_EPA").checked) ? 'True' : 'False';
    var use_teleop_EPA = (document.getElementById("use_TeleOp_EPA").checked) ? 'True' : 'False';
    var use_endgame_EPA = (document.getElementById("use_endgame_EPA").checked) ? 'True' : 'False';

    let res = await fetch(`/get_rankings?event=${$('#event_selection').val()}&OPR=${use_OPR}&CCWMS=${use_CCWMS}&Overall=${use_overall_EPA}&Auto=${use_auto_EPA}&Teleop=${use_teleop_EPA}&Endgame=${use_endgame_EPA}`);
    res = await res.text();

    $('#calculate_spinner').addClass('d-none');
    $('#calculate_label').removeClass('d-none');

    let resp = JSON.parse(res);

    names = resp[0];
    scores = resp[1];

    const ctx = document.getElementById('ranking_score').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: names,
            datasets: [{
                // axis: 'y',
                label: 'Ranking',
                data: scores,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                // indexAxis: 'y',
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

function search_team() {
    team = $('#team_search').val();
    console.log("runing");
    window.location.assign("https://youtube.com");
}

function change_flex() {
    $('#content').attr('style', 'display: flex; justify-content: center; align-items: center;');
}

function add_chat(chat, isBot) {

    var div = document.createElement('div');
    div.classList.add("d-flex");
    div.classList.add("flex-row");
    div.classList.add("p-3");
    if (isBot) {div.classList.add("justify-content-start");}
    else {div.classList.add("justify-content-end");}

    var div2 = document.createElement('div');
    div2.classList.add("bg-white")
    div2.classList.add("mr-2")
    div2.classList.add("p-3")

    var span = document.createElement('span');
    span.classList.add("text-muted");
    span.innerHTML = chat;

    var img = document.createElement('img');
    if (isBot) {img.src = "https://img.icons8.com/?size=512&id=102660&format=png";}
    else {img.src = "https://img.icons8.com/color/48/000000/circled-user-male-skin-type-7.png";}
    img.height = 30;
    img.width = 30;

    div2.append(span);
    if (isBot) {div.append(img); div.append(div2);;}
    else {div.append(div2); div.append(img);}

    $('#chats').append(div);
}

async function send_chat() {
    chat = $('#chat_input').val();
    add_chat(chat,false)

    let res = await fetch(`/chat_response?chat=${chat}`);
    res = await res.text();

    add_chat(res, true);
}