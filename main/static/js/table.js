// table lnst, eps rate 4 quarter ↑

// table bctc percent

// table highest, lowest

// Ajax Helpers
async function requestTableData(grid, selectedYear, btnId) {
  let content = {
    "selectedYear": selectedYear,
    "btnId": btnId
  };
  let response = await fetch('http://127.0.0.1:8000/filter_data_tbl/', {
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(content)
  })
  let res = await response.json()
  let data = res.data;
  let years = res.years;
  updateTable(grid, data, generateRateTableDef(years));
}

async function requestBSData(grid, selectedYear) {
  let content = {
    "selectedYear": selectedYear,
  };
  let response = await fetch('http://127.0.0.1:8000/filter_balance_sheet/', {
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(content)
  })
  let res = await response.json()
  let data = res.data;
  updateTable(grid, data, generateBSTableDef());
}

async function requestORData(grid, selectedYear) {
  let content = {
    "selectedYear": selectedYear,
  };
  let response = await fetch('http://127.0.0.1:8000/filter_operation_result/', { // need to change
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(content)
  })
  let res = await response.json()
  // let data = res.data;
  updateTable(grid, {}, {});
}

async function requestORData(grid, selectedYear) {
  let content = {
    "selectedYear": selectedYear,
  };
  let response = await fetch('http://127.0.0.1:8000/filter_financial_fig/', { // need to change
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(content)
  })
  let res = await response.json()
  // let data = res.data;
  updateTable(grid, {}, {});
}

// Constructor and Update Functions
function createGridInstance(id,expandFirstCol=false) {
  // return agGrid.createGrid(document.querySelector("#" + id), {});
  let element = document.querySelector("#" + id);
  let gridOptions;
  if (expandFirstCol){
    gridOptions = {
      onGridReady: function (params) {
        var columnIdsToAutoSize = [];
        var allDisplayedColumns = params.api.getAllDisplayedColumns();

        columnIdsToAutoSize.push(allDisplayedColumns[0].getColId());
        columnIdsToAutoSize.push(allDisplayedColumns[3].getColId());

        params.api.autoSizeColumns(columnIdsToAutoSize);
        
      }
    };
  }
  else {
    gridOptions = {
      onGridReady: function(params) {
        params.api.sizeColumnsToFit();
      }
    }
  }
  
  let grid = agGrid.createGrid(element, gridOptions);
  element.__ag_grid_instance = grid;
  return grid;
}

function updateTable(grid, data, columnDefs, expandFirstCol=false) {
  grid.setGridOption("columnDefs", columnDefs);
  grid.setGridOption("rowData", data);
  grid.setGridOption("rowDragManaged", true);
  if (expandFirstCol) {
    var allDisplayedColumns = grid.columnApi.getAllDisplayedColumns();
    columnIdsToAutoSize.push(allDisplayedColumns[0].getColId());
    columnIdsToAutoSize.push(allDisplayedColumns[3].getColId());
    grid.autoSizeColumns(columnIdsToAutoSize);
  } else {
    grid.sizeColumnsToFit();
  }
}

// Rate Table Helpers
function generateRateTableDef(years) {
  let columnDefs = [{ headerName: "", field: "quarter", rowDrag: true, minWidth: 50, maxWidth: 150, autoHeight: true }];
  let headerGroup = [];

  for (let i = 0; i < years.length; i++) {
    headerGroup.push({
      headerName: years[i],
      children: [
        {
          headerName: "Giá trị",
          field: years[i] + " value",
          type: "numericColumn",
          minWidth: 50,
          maxWidth: 150,
          autoHeight: true,
          valueFormatter: (params) => {
            if (params.value === undefined) {
              return params.value;
            }

            return params.value
              .toString()
              .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
          },
        },
        {
          headerName: "TT Cuối Kỳ",
          field: years[i] + " rate",
          type: "numericColumn",
          minWidth: 50,
          maxWidth: 150,
          autoHeight: true,
          cellStyle: (params) => {
            if (params.value < 0) {
              return { color: "red", fontWeight: "500" };
            }

            if (params.value > 0) {
              return { color: "#22cd22", fontWeight: "500" };
            }

            return null;
          },
          cellRenderer: function (params) {
            if (params.value === undefined) {
              return params.value;
            }

            let icon;

            if (params.value > 0) {
              icon = '<i class="fa fa-long-arrow-up"></i>';
            }

            if (params.value < 0) {
              icon = '<i class="fa fa-long-arrow-down"></i>';
            }

            return (params.value * 100).toFixed(2) + "%" + " " + icon;
          },
        },
      ],
    });
  }

  return columnDefs.concat(headerGroup);
}

function generateBSTableDef() {
  let columnDefs = [
    {
      headerName: "Tài sản",
      children: [
        {
          headerName: "",
          field: "name-1",
          sortable: false,
        },
        {
          headerName: "Giá trị",
          field: "value-1",
          valueFormatter: (params) => {
            if (params.value == undefined) {
              return params.value;
            }

            return params.value.v
              .toString()
              .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
          },
          cellStyle: (params) => {
            if (params.value == undefined) {
              return null;
            }

            if (params.value.c == 1) {
              return { color: "#22cd22", fontWeight: "500" };
            }

            if (params.value.c == -1) {
              return { color: "red", fontWeight: "500" };
            }

            return null;
          },
        },
        { headerName: "Ghi chú", field: "note-1", sortable: false },
      ],
    },
    {
      headerName: "Nguồn vốn",
      children: [
        {
          headerName: "",
          field: "name-2",
          sortable: false,
        },
        {
          headerName: "Giá trị",
          field: "value-2",
          valueFormatter: (params) => {
            if (params.value == undefined) {
              return params.value;
            }

            return params.value.v
              .toString()
              .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
          },
          cellStyle: (params) => {
            if (params.value == undefined) {
              return null;
            }

            if (params.value.c == 1) {
              return { color: "#22cd22", fontWeight: "500" };
            }

            if (params.value.c == -1) {
              return { color: "red", fontWeight: "500" };
            }

            return null;
          },
        },
        { headerName: "Ghi chú", field: "note-2", sortable: false },
      ],
    },
  ];

  return columnDefs;
}

