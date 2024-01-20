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
  let index;
  if (btnId == 'dropdownEPS'){
    index = 1;
  } else {
    index = 1e9;
  }
  updateTable(grid, data, generateRateTableDef(years,index));
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
  updateTable(grid, data, generateBSTableDef(), true);
}

async function requestORData(grid, selectedYear) {
  let content = {
    "selectedYear": selectedYear,
  };
  let response = await fetch('http://127.0.0.1:8000/filter_operation_result/', { 
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(content)
  })
  let res = await response.json()
  // let data = res.data;
  updateTable(grid, res.data, generateBRTableDef(res.years), true);
}

async function requestFFData(grid, selectedQuarter) {
  let content = {
    "selectedQuarter": selectedQuarter,
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
  updateTable(grid, res.data, generateFITableDef(res.stocks), false, true);
}

// Constructor and Update Functions
function createGridInstance(id, expandFirstCol = false, expandAllCol = false) {
  // return agGrid.createGrid(document.querySelector("#" + id), {});
  let element = document.querySelector("#" + id);
  let gridOptions;
  
  if (expandFirstCol) {
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
      onGridReady: function (params) {
        params.api.sizeColumnsToFit();
      }
    }
  }
  if (expandAllCol){
    gridOptions = {
      onGridReady: function (params) {
        params.api.autoSizeAllColumns();
      }
    }
  }
  let grid = agGrid.createGrid(element, gridOptions);
  element.__ag_grid_instance = grid;
  window.addEventListener('resize', function() {
    grid.autoSizeAllColumns();
  });

  return grid;
}

function updateTable(grid, data, columnDefs, expandFirstCol = false, expandAllCol = false) {
  grid.setGridOption("columnDefs", columnDefs);
  grid.setGridOption("rowData", data);
  grid.setGridOption("rowDragManaged", true);
  var columnIdsToAutoSize = [];

  if (expandAllCol){
    grid.autoSizeAllColumns();
    return;
  }
  if (expandFirstCol) {
    var allDisplayedColumns = grid.getAllDisplayedColumns();
    columnIdsToAutoSize.push(allDisplayedColumns[0].getColId());
    columnIdsToAutoSize.push(allDisplayedColumns[3].getColId());
    grid.autoSizeColumns(columnIdsToAutoSize);
  } else {
    grid.sizeColumnsToFit();
  }
}

// Rate Table Helpers
function generateRateTableDef(years, index) {
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
            let formatted;
            if (index !== 1){
              let parts = (params.value / index).toFixed(3).split('.');
              formatted = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '.' + parts[1];
            }
            else {
              formatted = params.value.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
            }

            return formatted;
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
          autoHeight: true,
          rowDrag: true,
        },
        {
          headerName: "Giá trị",
          field: "value-1",
          type: "numericColumn",
          valueFormatter: (params) => {
            if (params.value == undefined) {
              return params.value;
            }
            if (params.value.v === 0){
              formatted = 0;
            } 
            else {
              let parts = (params.value.v / 1e9).toFixed(3).split('.');
              formatted = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '.' + parts[1];
            }
            return formatted;
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
        {
          headerName: "Ghi chú",
          field: "note-1",
          sortable: false,
          autoHeight: true,
        },
      ],
    },
    {
      headerName: "Nguồn vốn",
      children: [
        {
          headerName: "",
          field: "name-2",
          sortable: false,
          autoHeight: true,
        },
        {
          headerName: "Giá trị",
          field: "value-2",
          type: "numericColumn",
          valueFormatter: (params) => {
            if (params.value == undefined) {
              return params.value;
            }
            if (params.value.v === 0){
              formatted = 0;
            } 
            else {
              let parts = (params.value.v / 1e9).toFixed(3).split('.');
              formatted = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '.' + parts[1];
            }
            return formatted;
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
        {
          headerName: "Ghi chú",
          field: "note-2",
          sortable: false,
          autoHeight: true,
        },
      ],
    },
  ];

  return columnDefs;
}

function generateBRTableDef(years) {
  let columnDefs = [
    {
      headerName: "",
      field: "name",
      sortable: false,
      rowDrag: true,
      autoHeight: true,
    },
    {
      headerName: years[0],
      field: "value-1",
      type: "numericColumn",
      autoHeight: true,
      valueFormatter: (params) => {
        if (params.value == undefined) {
          return params.value;
        }
        if (params.value === 0){
          formatted = 0;
        } 
        else {
          let parts = (params.value / 1e9).toFixed(3).split('.');
          formatted = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '.' + parts[1];
        }
        return formatted;
      },
    },
    {
      headerName: "Ghi chú",
      field: "note-1",
      sortable: false,
      valueFormatter: (params) => {
        if (params.value == undefined) {
          return params.value;
        }

        return params.value.v;
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
    {
      headerName: years[1],
      field: "value-2",
      type: "numericColumn",
      autoHeight: true,
      cellStyle: (params) => {
        if (params.data["value-1"] > params.value) {
          return { color: "red", fontWeight: "500" };
        }

        if (params.data["value-1"] < params.value) {
          return { color: "green", fontWeight: "500" };
        }

        return null;
      },
      cellRenderer: function (params) {
        if (params.value === undefined) {
          return params.value;
        }

        let icon;
        if (params.value === 0){
          formatted = 0;
        } 
        else{
          let parts = (params.value / 1e9).toFixed(3).split('.');
          formatted = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '.' + parts[1];
        }
        if (params.data["value-1"] < params.value) {
          icon = '<i class="fa fa-long-arrow-up"></i>';
        }
        if (params.data["value-1"] > params.value) {
          icon = '<i class="fa fa-long-arrow-down"></i>';
        }
        if (params.data["value-1"] == params.value) {
          icon = '';
        }

        return (
          formatted +
          " " +
          icon
        );
      },
    },
    {
      headerName: "Ghi chú",
      field: "note-2",
      sortable: false,
      autoHeight: true,
      valueFormatter: (params) => {
        if (params.value == undefined) {
          return params.value;
        }

        return params.value.v;
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
  ];

  return columnDefs;
}

function generateFITableDef(stocks) {
  let columnDefs = [
    {
      headerName: "Chỉ số",
      field: "index",
      rowDrag: true,
      minWidth: 50,
      // maxWidth: 150,
      autoHeight: true,
    },
  ];

  let headerGroup = [];

  for (let i = 0; i < stocks.length; i++) {
    headerGroup.push({
      headerName: stocks[i],
      field: stocks[i],
      type: "numericColumn",
      minWidth: 50,
      // maxWidth: 150,
      autoHeight: true,
      valueFormatter: (params) => {
        if (params.value == undefined) {
          return params.value;
        }

        if (
          params.data["index"] == "ROS" ||
          params.data["index"] == "ROA" ||
          params.data["index"] == "ROE" ||
          params.data["index"] == "ROIC" ||
          params.data["index"] == "Nợ/TS"
        ) {
          if (parseFloat((params.value * 100).toFixed(2)) == 0) {
            return 0 + "%";
          }

          return (params.value * 100).toFixed(2) + "%";
        }

        if (parseFloat(params.value.toFixed(3)) == 0) {
          return 0;
        }

        let parts = params.value.toFixed(3).split(".");
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        return parts.join(".");
      },
      cellStyle: (params) => {
        if (params.value == undefined) {
          return null;
        }

        objValues = Object.values(params.data).filter((v) => {
          if (typeof v == "number") {
            return v;
          }
        });

        if (
          params.data["index"] == "Nợ/TS" ||
          params.data["index"] == "Đòn bẩy tài chính"
        ) {
          if (params.value == Math.max(...objValues)) {
            return { color: "red", fontWeight: "500" };
          }

          if (params.value == Math.min(...objValues)) {
            return { color: "#22cd22", fontWeight: "500" };
          }
        } else {
          if (params.value == Math.max(...objValues)) {
            return { color: "#22cd22", fontWeight: "500" };
          }

          if (params.value == Math.min(...objValues)) {
            return { color: "red", fontWeight: "500" };
          }
        }

        return null;
      },
    });
  }

  return columnDefs.concat(headerGroup);
}
