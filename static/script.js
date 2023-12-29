(() => {
  "use strict";

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll(".needs-validation");

  // Loop over them and prevent submission
  Array.from(forms).forEach((form) => {
    form.addEventListener(
      "submit",
      (event) => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }

        form.classList.add("was-validated");
      },
      false
    );
  });
})();

var team = 492;

async function get_events() {
  let res = await fetch(
    `/api/get_events?season=${$("#season_selection").val()}&team_number=${$(
      "#team_number"
    ).val()} `
  );
  res = await res.text();

  $("#event_selection_form").removeClass("d-none");
  $("#event_selection").empty();

  var resp = JSON.parse(res);

  resp.forEach((element) => {
    var opt = document.createElement("option");
    opt.value = element[1];
    opt.innerHTML = element[0];
    $("#event_selection").append(opt);
  });
}

async function get_rankings() {
  $("#calculate_spinner").removeClass("d-none");
  $("#calculate_label").addClass("d-none");

  var use_OPR = document.getElementById("use_OPR").checked ? "True" : "False";
  var use_CCWMS = document.getElementById("use_CCWMS").checked
    ? "True"
    : "False";
  var use_overall_EPA = document.getElementById("use_overall_EPA").checked
    ? "True"
    : "False";
  var use_auto_EPA = document.getElementById("use_auto_EPA").checked
    ? "True"
    : "False";
  var use_teleop_EPA = document.getElementById("use_TeleOp_EPA").checked
    ? "True"
    : "False";
  var use_endgame_EPA = document.getElementById("use_endgame_EPA").checked
    ? "True"
    : "False";

  let res = await fetch(
    `/api/get_rankings?event=${$(
      "#event_selection"
    ).val()}&OPR=${use_OPR}&CCWMS=${use_CCWMS}&Overall=${use_overall_EPA}&Auto=${use_auto_EPA}&Teleop=${use_teleop_EPA}&Endgame=${use_endgame_EPA}`
  );
  res = await res.text();

  $("#calculate_spinner").addClass("d-none");
  $("#calculate_label").removeClass("d-none");

  let resp = JSON.parse(res);

  names = resp[0];
  console.log(names);
  scores = resp[1];

  if (document.getElementById("ranking_score").style["display"] == "") {
    const ctx = document.getElementById("ranking_score").getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: names,
        datasets: [
          {
            // axis: 'y',
            label: "Ranking",
            data: scores,
            borderWidth: 1,
          },
        ],
      },
      options: {
        scales: {
          // indexAxis: 'y',
          x: {
            beginAtZero: true,
          },
        },
      },
    });
  } else {
    chart = Chart.getChart("ranking_score");
    removeData(chart);
    addData(chart, names, scores);
  }
}

function addData(chart, label, newData) {
  chart.data.labels = label;
  chart.data.datasets[0].data = newData;
  chart.update();
}

function removeData(chart) {
  chart.data.labels = [];
  chart.data.datasets[0].data = [];
}

function search_team() {
  team = $("#team_search").val();
  window.location.assign("/team/" + team);
}

function change_flex() {
  $("#content").attr(
    "style",
    "display: flex; justify-content: center; align-items: center;"
  );
}

function add_chat(chat, isBot) {
  var div = document.createElement("div");
  div.classList.add("d-flex");
  div.classList.add("flex-row");
  div.classList.add("p-3");
  if (isBot) {
    div.classList.add("justify-content-start");
  } else {
    div.classList.add("justify-content-end");
  }

  var div2 = document.createElement("div");
  div2.classList.add("bg-white");
  div2.classList.add("mr-2");
  div2.classList.add("p-3");

  var span = document.createElement("span");
  span.classList.add("text-muted");
  span.innerHTML = chat;

  var img = document.createElement("img");
  if (isBot) {
    img.src = "https://img.icons8.com/?size=512&id=102660&format=png";
  } else {
    img.src =
      "https://img.icons8.com/color/48/000000/circled-user-male-skin-type-7.png";
  }
  img.height = 30;
  img.width = 30;

  div2.append(span);
  if (isBot) {
    div.append(img);
    div.append(div2);
  } else {
    div.append(div2);
    div.append(img);
  }

  $("#chats").append(div);

  var objDiv = document.getElementById("chats");
  objDiv.scrollTop = objDiv.scrollHeight;
}

async function send_chat() {
  chat = $("#chat_input").val();
  add_chat(chat, false);

  let res = await fetch(`/api/chat_response?chat=${chat}`);
  res = await res.text();

  add_chat(res, true);
}
