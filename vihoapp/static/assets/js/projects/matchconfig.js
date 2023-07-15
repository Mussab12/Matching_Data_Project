document.addEventListener("DOMContentLoaded", () => {
  // Handle the click event of the "All" button
  matchConfig("select-all", [
    "customer_master",
    "customermaster_record",
    "newprospect_record",
  ]);
  matchConfig("select-within", ["customer_master"]);
  matchConfig("select-between", ["customermaster_record"]);
  matchConfig("select-none", [
    "customer_master",
    "customermaster_record",
    "newprospect_record",
  ]);
});

const getColumnnames = async () => {
  try {
    const response = await fetch("/apis/v1/getmodelname/", {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });
    const data = await response.json();

    console.log(data);

    document.querySelector("tbody tr:nth-child(1) td:nth-child(1)").innerHTML =
      data[0];
    document.querySelector("tbody tr:nth-child(2) td:nth-child(1)").innerHTML =
      data[1];

    const thead = document.querySelector("thead");
    thead.innerHTML = "";

    const emptyTh = document.createElement("th");
    thead.appendChild(emptyTh);

    data.forEach((item) => {
      const th = document.createElement("th");
      th.textContent = item;
      thead.appendChild(th);
    });
  } catch (error) {
    console.error(error);
  }
};

getColumnnames();

// Match Config Validation
const matchConfig = (buttonId, checkboxIds) => {
  const button = document.getElementById(buttonId);
  const checkboxes = checkboxIds.map((id) => document.getElementById(id));

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener(
      "change",
      debounce(() => {
        updateCheckedValues(checkbox, checkboxes);
      }, 300)
    ); // 300 milliseconds delay
  });

  button.onclick = (event) => {
    event.preventDefault();
    matchButtonValidate(buttonId, checkboxes);
  };
};

const debounce = (func, delay) => {
  let timerId;
  return (...args) => {
    clearTimeout(timerId);
    timerId = setTimeout(() => {
      func.apply(null, args);
    }, delay);
  };
};

const matchButtonValidate = (buttonId, checkboxes) => {
  const checked = buttonId !== "select-none";
  const checkedValues = [];
  checkboxes.forEach((checkbox) => {
    checkbox.checked = checked;
    if (checkbox.checked) {
      checkedValues.push(checkbox.id); // Store the checkbox ID instead of the value
    }
  });
  console.log(checkedValues);
  saveMatchingConfig(checkedValues);
  return checkedValues; // Return the array of checked checkbox IDs
};
const updateCheckedValues = (changedCheckbox, checkboxes) => {
  const checkedValues = checkboxes
    .filter((checkbox) => checkbox.checked)
    .map((checkbox) => checkbox.id);

  console.log(checkedValues);
  saveMatchingConfig(checkedValues);
};

const saveMatchingConfig = (checkedValues) => {
  // Send the checkedValues to the API endpoint
  const csrftoken = getCookie("csrftoken");

  fetch("/apis/v1/matchconfig/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken, // Include the CSRF token in the request headers
    },
    body: JSON.stringify({ checked_values: checkedValues }), // Convert the array to JSON and send it in the request body
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Matching configuration saved:", data);
      // Handle the API response here

      // Perform GET request to retrieve the response
      fetch("/apis/v1/matchconfig/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken, // Include the CSRF token in the request headers
        },
      })
        .then((response) => response.json())
        .then((getData) => {
          console.log("Matching configuration retrieved:", getData);
          // Handle the GET API response here
        })
        .catch((error) => {
          console.error("Error retrieving matching configuration:", error);
        });
    })
    .catch((error) => {
      console.error("Error saving matching configuration:", error);
    });
};

// Exporting xlsx

document
  .getElementById("fileForm")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent form submission

    var fileInput = document.getElementById("xlsxFile");
    var file = fileInput.files[0]; // Get the selected file

    var formData = new FormData();
    formData.append("xlsxFile", file); // Append the file to the form data

    // Get the CSRF token
    var csrfToken = getCookie("csrftoken");

    // Set up the AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/apis/v1/exceltojson/", true); // Replace with your API endpoint

    // Set the CSRF token header
    xhr.setRequestHeader("X-CSRFToken", csrfToken);

    xhr.onload = function () {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        console.log(response); // Handle the API response
      } else {
        console.error("Error:", xhr.status);
      }
    };

    xhr.send(formData);
  });

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
