
// Generate component
async function generateRateTableComponent() {

  const epsContainer = document.getElementById('eps_analysis');
  const salesContainer = document.getElementById('sales_analysis');
  const npatContainer = document.getElementById('npat_analysis');

  // Reset
  epsContainer.innerHTML = '';
  salesContainer.innerHTML = '';
  npatContainer.innerHTML = '';

  try {
    let epsOptions = '';
    let npatOptions = ''; 
    let salesOptions = '';
    const response = await fetch('http://127.0.0.1:8000/get_rate_table/',{
      method : "POST",
      headers: {
        'Content-Type': 'application/json'
      },
    })

    let dataYears = await response.json();
    
    let years_eps = dataYears.dropdown_json.yearsFrq;
    let years_npat = dataYears.dropdown_json.yearsNpat;
    let years_sales = dataYears.dropdown_json.yearsSales;

    years_eps.forEach((year) => {
      epsOptions += `<a class="analysis-options dropdown-item">${year}</a>`;
    });

    years_npat.forEach((year) => {
      npatOptions += `<a class="analysis-options dropdown-item">${year}</a>`;
    });

    years_sales.forEach((year) => {
      salesOptions += `<a class="analysis-options dropdown-item">${year}</a>`;
    });
    for (let i = 0; i <= 2; i++){
      let lastOption;
      let dropdownId, tableId = '';
      let container;
      let dropdownMenu = document.createElement("div");
      dropdownMenu.className = "dropdown-menu";

      if (i == 0){
        lastOption = years_eps.slice(-1);
        dropdownId = "dropdownEPS";
        tableId = "eps_table";
        container = epsContainer;
        dropdownMenu.innerHTML = epsOptions;
      }
      else if (i == 1){
        lastOption = years_npat.slice(-1);
        dropdownId = "dropdownNpat";
        tableId = "npat_table";
        container = npatContainer;
        dropdownMenu.innerHTML = npatOptions;

      } else if (i == 2){
        lastOption = years_sales.slice(-1);
        dropdownId = "dropdownSales";
        tableId = "sales_table";
        container = salesContainer;
        dropdownMenu.innerHTML = salesOptions;
      }

      let dropdownContainer = document.createElement("div");
      dropdownContainer.className = "btn-group";

      let dropdownButton = document.createElement("button");
      dropdownButton.id = dropdownId;
      dropdownButton.type = "button";
      dropdownButton.className = "btn btn-primary";
      dropdownButton.innerText = lastOption;

      let dropdownToggleButton = document.createElement("button");
      dropdownToggleButton.type = "button";
      dropdownToggleButton.className =
        "btn btn-primary dropdown-toggle dropdown-toggle-split";
      dropdownToggleButton.setAttribute("data-bs-toggle", "dropdown");
      dropdownToggleButton.setAttribute("aria-expanded", "false");

      let span = document.createElement("span");
      span.className = "sr-only";
      span.innerText = "Toggle Dropdown";

      dropdownToggleButton.appendChild(span);
      dropdownContainer.appendChild(dropdownButton);
      dropdownContainer.appendChild(dropdownToggleButton);
      dropdownContainer.appendChild(dropdownMenu);

      let space = document.createElement("div");
      space.className = "mb-2";

      let table = document.createElement("div");
      table.id = tableId;
      table.className = "ag-theme-quartz-dark";
      table.style.cssText = "height: 400px; width: 100%;";

      container.appendChild(dropdownContainer);
      container.appendChild(space);
      container.appendChild(table);

      let gridInstance = createGridInstance(tableId);
      if (i == 0){
        updateTable(
          gridInstance,
          dataYears.frq_data,
          generateRateTableDef(dataYears.frq_years,1)
        );
      }
      else if (i == 1){
        updateTable(
          gridInstance,
          dataYears.npat_data,
          generateRateTableDef(dataYears.npat_years,1e9)
        );

      } else if (i == 2){
        updateTable(
          gridInstance,
          dataYears.sales_data,
          generateRateTableDef(dataYears.sales_years,1e9)
        );
      }
    }
    document.querySelectorAll('.analysis-options').forEach(option => {
      option.addEventListener('click', async function (e) {
        var currentElement = e.target;
        var selectedYear = currentElement.innerText;
    
        var commonAncestor = currentElement.closest('.btn-group');
        if (commonAncestor) {
          var dropdownElement = commonAncestor.querySelector('[id^="dropdown"]');
          if (dropdownElement) {
            var btnId = dropdownElement.id;
            document.getElementById(btnId).innerText = selectedYear;
            await dropDownRateTable(selectedYear, btnId);
          }
        }
      });
    });
    
  } catch (error) {
    console.error("Error:", error);
  }
}
async function generateBalanceSheet() {

  const balanceSheetContainer = document.getElementById('balance_sheet');
  balanceSheetContainer.innerHTML = '';
  try {
    let bsOptions = '';
    const response = await fetch('http://127.0.0.1:8000/get_balance_sheet/',{
      method : "POST",
      headers: {
        'Content-Type': 'application/json'
      },
    })

    let dataYears = await response.json();
    
    let years = dataYears.years; 

    years.forEach((year) => {
      bsOptions += `<a class="bs-options dropdown-item">${year}</a>`;
    });

    let dropdownId, tableId = '';
    let container;
    let dropdownMenu = document.createElement("div");
    dropdownMenu.className = "dropdown-menu";

    dropdownId = "dropdownBS";
    tableId = "bs_table";
    container = balanceSheetContainer;
    dropdownMenu.innerHTML = bsOptions;

    let dropdownContainer = document.createElement("div");
    dropdownContainer.className = "btn-group";

    let dropdownButton = document.createElement("button");
    dropdownButton.id = dropdownId;
    dropdownButton.type = "button";
    dropdownButton.className = "btn btn-primary";
    dropdownButton.innerText = years.slice(-1);

    let dropdownToggleButton = document.createElement("button");
    dropdownToggleButton.type = "button";
    dropdownToggleButton.className = "btn btn-primary dropdown-toggle dropdown-toggle-split";
    dropdownToggleButton.setAttribute("data-bs-toggle", "dropdown");
    dropdownToggleButton.setAttribute("aria-expanded", "false");

    let span = document.createElement("span");
    span.className = "sr-only";
    span.innerText = "Toggle Dropdown";

    dropdownToggleButton.appendChild(span);
    dropdownContainer.appendChild(dropdownButton);
    dropdownContainer.appendChild(dropdownToggleButton);
    dropdownContainer.appendChild(dropdownMenu);

    let space = document.createElement("div");
    space.className = "mb-2";

    let table = document.createElement("div");
    table.id = tableId;
    table.className = "ag-theme-quartz-dark";
    table.style.cssText = "height: 400px; width: 100%;";

    container.appendChild(dropdownContainer);
    container.appendChild(space);
    container.appendChild(table);

    let gridInstance = createGridInstance(tableId, true);

    updateTable(
      gridInstance,
      dataYears.data,
      generateBSTableDef()
    );
    document.querySelectorAll('.bs-options').forEach(option => {
      option.addEventListener('click', async function (e) {
        var currentElement = e.target;
        var selectedYear = currentElement.innerText;
    
        var commonAncestor = currentElement.closest('.btn-group');
        if (commonAncestor) {
          var dropdownElement = commonAncestor.querySelector('[id^="dropdown"]');
          if (dropdownElement) {
            var btnId = dropdownElement.id;
            document.getElementById(btnId).innerText = selectedYear;
            await dropdownBSTable(selectedYear,'bs_table');
          }
        }
      });
    });
    
  } catch (error) {
    console.error("Error:", error);
  }
}

async function generateOperationResult() {

  const balanceSheetContainer = document.getElementById('operation_result');
  balanceSheetContainer.innerHTML = '';
  try {
    let bsOptions = '';
    const response = await fetch('http://127.0.0.1:8000/get_operation_result/',{
      method : "POST",
      headers: {
        'Content-Type': 'application/json'
      },
    })

    let dataYears = await response.json();
    
    let years = dataYears.dropdown_json;
    years.forEach((year) => {
      bsOptions += `<a class="or-options dropdown-item">${year}</a>`;
    });

    let dropdownId, tableId = '';
    let container;
    let dropdownMenu = document.createElement("div");
    dropdownMenu.className = "dropdown-menu";

    dropdownId = "dropdownOR";
    tableId = "or_table";
    container = balanceSheetContainer;
    dropdownMenu.innerHTML = bsOptions;

    let dropdownContainer = document.createElement("div");
    dropdownContainer.className = "btn-group";

    let dropdownButton = document.createElement("button");
    dropdownButton.id = dropdownId;
    dropdownButton.type = "button";
    dropdownButton.className = "btn btn-primary";
    dropdownButton.innerText = years.slice(-1);

    let dropdownToggleButton = document.createElement("button");
    dropdownToggleButton.type = "button";
    dropdownToggleButton.className = "btn btn-primary dropdown-toggle dropdown-toggle-split";
    dropdownToggleButton.setAttribute("data-bs-toggle", "dropdown");
    dropdownToggleButton.setAttribute("aria-expanded", "false");

    let span = document.createElement("span");
    span.className = "sr-only";
    span.innerText = "Toggle Dropdown";

    dropdownToggleButton.appendChild(span);
    dropdownContainer.appendChild(dropdownButton);
    dropdownContainer.appendChild(dropdownToggleButton);
    dropdownContainer.appendChild(dropdownMenu);

    let space = document.createElement("div");
    space.className = "mb-2";

    let table = document.createElement("div");
    table.id = tableId;
    table.className = "ag-theme-quartz-dark";
    table.style.cssText = "height: 400px; width: 100%;";

    container.appendChild(dropdownContainer);
    container.appendChild(space);
    container.appendChild(table);

    let gridInstance = createGridInstance(tableId, false,false);

    updateTable(
      gridInstance,
      dataYears.data,
      generateBRTableDef(dataYears.years)
    );
    document.querySelectorAll('.or-options').forEach(option => {
      option.addEventListener('click', async function (e) {
        var currentElement = e.target;
        var selectedYear = currentElement.innerText;
    
        var commonAncestor = currentElement.closest('.btn-group');
        if (commonAncestor) {
          var dropdownElement = commonAncestor.querySelector('[id^="dropdown"]');
          if (dropdownElement) {
            var btnId = dropdownElement.id;
            document.getElementById(btnId).innerText = selectedYear;
            await dropdownOR(selectedYear,'or_table');
          }
        }
      });
    });
    
  } catch (error) {
    console.error("Error:", error);
  }
}

async function generateFinancialFig() {
  const balanceSheetContainer = document.getElementById('financial-tbl');
  balanceSheetContainer.innerHTML = '';
  try {
    let bsOptions = '';
    const response = await fetch('http://127.0.0.1:8000/get_financial_fig/',{
      method : "POST",
      headers: {
        'Content-Type': 'application/json'
      },
    })

    let dataYears = await response.json();
    
    let options = dataYears.dropdown_json; 

    options.forEach((option) => {
      bsOptions += `<a class="ff-options dropdown-item">${option}</a>`;
    });

    let dropdownId, tableId = '';
    let container;
    let dropdownMenu = document.createElement("div");
    dropdownMenu.className = "dropdown-menu";

    dropdownId = "dropdownFF";
    tableId = "financial_table";
    container = balanceSheetContainer;
    dropdownMenu.innerHTML = bsOptions;

    let dropdownContainer = document.createElement("div");
    dropdownContainer.className = "btn-group d-block";

    let dropdownButton = document.createElement("button");
    dropdownButton.id = dropdownId;
    dropdownButton.type = "button";
    dropdownButton.className = "btn btn-primary";
    dropdownButton.innerText = options.slice(-1);

    let dropdownToggleButton = document.createElement("button");
    dropdownToggleButton.type = "button";
    dropdownToggleButton.className = "btn btn-primary dropdown-toggle dropdown-toggle-split";
    dropdownToggleButton.setAttribute("data-bs-toggle", "dropdown");
    dropdownToggleButton.setAttribute("aria-expanded", "false");

    let span = document.createElement("span");
    span.className = "sr-only";
    span.innerText = "Toggle Dropdown";

    dropdownToggleButton.appendChild(span);
    dropdownContainer.appendChild(dropdownButton);
    dropdownContainer.appendChild(dropdownToggleButton);
    dropdownContainer.appendChild(dropdownMenu);

    let space = document.createElement("div");
    space.className = "mb-2";

    let table = document.createElement("div");
    table.id = tableId;
    table.className = "ag-theme-quartz-dark";
    table.style.cssText = "height: 400px; width: 100%;";

    container.appendChild(dropdownContainer);
    container.appendChild(space);
    container.appendChild(table);

    let gridInstance = createGridInstance(tableId, true);

    updateTable(
      gridInstance,
      dataYears.data,
      generateFITableDef(dataYears.stocks)
    );
    document.querySelectorAll('.ff-options').forEach(option => {
      option.addEventListener('click', async function (e) {
        var currentElement = e.target;
        var selectedYear = currentElement.innerText;
    
        var commonAncestor = currentElement.closest('.btn-group');
        if (commonAncestor) {
          var dropdownElement = commonAncestor.querySelector('[id^="dropdown"]');
          if (dropdownElement) {
            var btnId = dropdownElement.id;
            document.getElementById(btnId).innerText = selectedYear;
            await dropdownFinancialFig(selectedYear,'financial_table');
          }
        }
      });
    });
    
  } catch (error) {
    console.error("Error:", error);
  }
}

// Event function
async function dropDownRateTable(selectedItem, btnId) {
  let tableId = '';
  if (btnId == "dropdownEPS"){
    tableId = 'eps_table'
  }
  else if (btnId == "dropdownNpat"){
    tableId = "npat_table";
  } else if (btnId == "dropdownSales"){
    tableId = "sales_table";
  }
  let tableRate = document.getElementById(tableId);
  await requestTableData(tableRate.__ag_grid_instance,selectedItem, btnId);
}

async function dropdownBSTable(selectedItem, tableId) {
  let tableRate = document.getElementById(tableId);
  await requestBSData(tableRate.__ag_grid_instance,selectedItem);
}

async function dropdownOR(selectedItem, tableId) {
  let tableRate = document.getElementById(tableId);
  await requestORData(tableRate.__ag_grid_instance,selectedItem);
}

async function dropdownFinancialFig(selectedItem, tableId) {
  let tableRate = document.getElementById(tableId);
  await requestFFData(tableRate.__ag_grid_instance,selectedItem);
}