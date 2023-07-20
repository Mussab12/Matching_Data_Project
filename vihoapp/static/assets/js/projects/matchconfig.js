let checkboxesArray = [];

// Generating table
const generateTable = (data) => {
  const tableContainer = document.getElementById("table-container");
  const existingTable = tableContainer.querySelector("table");
  if (existingTable) {
    tableContainer.removeChild(existingTable);
  }
  const table = document.createElement("table");
  table.className = "table table-bordered";
  // Create the header row (th) and populate it with IDs
  let headerRow = document.createElement("tr");
  // Add an empty cell in the first iteration (index = 0) to maintain alignment
  headerRow.appendChild(document.createElement("th"));
  headerRow = createHeaderRow(headerRow, data);
  table.appendChild(headerRow);
  checkboxesArray = []; // Reset the array when generating a new table
  // Create table rows (tr) for each data object (start from index 0)
  for (let i = 0; i < data.length; i++) {
    const col = data[i];
    const row = createRowWithCheckboxes(i, col.id);
    checkboxesArray.push(row.querySelectorAll('input[type="checkbox"]')); // Store the checkboxes in the array
    // Create the first cell (td) to display the ID
    table.appendChild(row);
  }
  tableContainer.appendChild(table);
  const buttonPatterns = {
    "select-between": "between",
    "select-within": "within",
    "select-none": "none",
    "select-all": "all",
    // Add more buttons and their patterns here as needed
  };

  Object.entries(buttonPatterns).forEach(([buttonId, pattern]) => {
    document.getElementById(buttonId).onclick = (event) => {
      event.preventDefault();
      const rowCount = data.length; // Replace this with the actual row count
      const colCount = data.reduce((max, col) => Math.max(max, col.id), 0); // Assuming 'id' is the number of columns

      const checkboxIdsToCheck = generateCheckboxIds(
        rowCount,
        colCount,
        pattern
      );
      checkAllCheckboxes(checkboxIdsToCheck, pattern);
      let checkedIds = getCheckedCheckboxIds(checkboxIdsToCheck, pattern);
      console.log(checkedIds);
      const checkboxes = document.querySelectorAll(".checkbox-item");

      checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
          updateCheckedIds(pattern); // Update the checkedIds array whenever a checkbox is manually checked or unchecked
          saveMatchingConfig(checkedIds);
        });
        const updateCheckedIds = (pattern) => {
          const rowCount = data.length; // Replace this with the actual row count
          const colCount = data.reduce((max, col) => Math.max(max, col.id), 0); // Assuming 'id' is the number of columns
          const checkboxIdsToCheck = generateCheckboxIds(
            rowCount,
            colCount,
            pattern
          ); // You can change the pattern if needed
          checkedIds = getCheckedCheckboxIds(checkboxIdsToCheck, pattern); // You can change the pattern if needed
          console.log(checkedIds);
        };
      });
      saveMatchingConfig(checkedIds);
    };
  });
};

// Function to generate checkbox IDs based on row and column numbers and the pattern
const generateCheckboxIds = (rowCount, colCount, pattern) => {
  if (pattern === "between") {
    return Array.from({ length: rowCount - 1 }, (_, i) =>
      Array.from(
        { length: Math.min(colCount, i + 1) },
        (_, j) => `row-${i + 2}-col-${j + 1}`
      )
    ).flat();
  } else if (pattern === "within") {
    return Array.from(
      { length: Math.min(rowCount, colCount) },
      (_, i) => `row-${i + 1}-col-${i + 1}`
    );
  } else if (pattern === "none") {
    return Array.from({ length: rowCount }, (_, i) =>
      Array.from(
        { length: Math.min(colCount, i + 1) },
        (_, j) => `row-${i + 1}-col-${j + 1}`
      )
    ).flat();
  } else if (pattern === "all") {
    return Array.from({ length: rowCount }, (_, i) =>
      Array.from(
        { length: Math.min(colCount, i + 1) },
        (_, j) => `row-${i + 1}-col-${j + 1}`
      )
    ).flat();
  }
  return [];
};

// Function to get the IDs of checked checkboxes based on their IDs and the pattern
const getCheckedCheckboxIds = (checkboxIds, pattern) => {
  const checkedIds = [];
  checkboxIds.forEach((checkboxId) => {
    const checkbox = document.getElementById(checkboxId);
    if (checkbox && checkbox.checked && pattern !== "none") {
      checkedIds.push(checkboxId);
    }
  });
  return checkedIds;
};
const checkAllCheckboxes = (checkboxIds, pattern) => {
  checkboxIds.forEach((checkboxId) => {
    const checkbox = document.getElementById(checkboxId);
    if (checkbox) {
      checkbox.checked = pattern !== "none";
    }
  });
};
// Function to create a checkbox element
const createCheckbox = (name, id) => {
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.classList = "checkbox-item";
  checkbox.name = name;
  checkbox.id = id;
  return checkbox;
};
// Dynamically Creating Checkboxes
// Function to create a row (tr) with checkboxes
const createRowWithCheckboxes = (rowIndex, numOfCheckboxes) => {
  const row = document.createElement("tr");

  // Create the first cell (td) to display the ID
  const idCell = document.createElement("td");
  idCell.innerText = `data ${rowIndex + 1}`;
  row.appendChild(idCell);

  // Add the checkboxes to subsequent cells (td) within the row
  for (let j = 0; j < numOfCheckboxes; j++) {
    const cell = document.createElement("td");

    // Use the createCheckbox function to create checkboxes
    const checkboxName = `row-${rowIndex + 1}-col-${j + 1}`;
    const checkboxId = `row-${rowIndex + 1}-col-${j + 1}`;
    const checkbox = createCheckbox(checkboxName, checkboxId);

    cell.appendChild(checkbox);
    row.appendChild(cell);
  }

  return row;
};
// Creating table header row
const createHeaderRow = (headerRow, data) => {
  for (let i = 0; i < data.length; i++) {
    const headerCell = document.createElement("th");
    headerCell.innerText = `data${data[i].id}`;
    headerRow.appendChild(headerCell);
  }
  return headerRow;
};
const getColumnnames = async () => {
  try {
    const response = await fetch("/apis/v1/exceltojson/", {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });
    const data = await response.json();
    generateTable(data);
  } catch (error) {
    console.error("Error fetching data from API:", error);
  }
};

window.onload = async () => {
  try {
    await getColumnnames();
  } catch (error) {
    console.error("Error fetching data and generating table:", error);
  }
};

const matchConfig = (buttonId, checkboxIds) => {
  const button = document.getElementById(buttonId);
  const checkboxes = checkboxIds.map((id) => document.getElementById(id));

  button.onclick = (event) => {
    event.preventDefault();
    matchButtonValidate(buttonId, checkboxes);
  };
};

const matchButtonValidate = (buttonId, checkboxes) => {
  const checked = buttonId !== "select-none";
  const checkedValues = [];

  checkboxes.forEach((checkbox) => {
    checkbox.checked = checked;
    if (checkbox.checked) {
      checkedValues.push(checkbox.id);
    }
  });

  console.log(checkedValues);
  saveMatchingConfig(checkedValues);
  return checkedValues;
};

const updateCheckboxArray = (checkboxes) => {
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

document.getElementById("fileForm").onsubmit = async (event) => {
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

  xhr.onload = async () => {
    if (xhr.status === 200) {
      var response = JSON.parse(xhr.responseText);
      console.log(response); // Handle the API response
      await getColumnnames();
    } else {
      console.error("Error:", xhr.status);
    }
  };

  xhr.send(formData);
};

// Getting Cookie name for post request
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
