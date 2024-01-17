function inputHandler(){
    const inputField = document.querySelector('.chosen-value');
    const dropdown = document.querySelector('.tickers-list');
    const dropdownArray = [...document.querySelectorAll('.ticker')];
    const backdrop = document.querySelector('.backdrop');

    let valueArray = [];
    dropdownArray.forEach(item => {
        valueArray.push(item.textContent);
    });

    const closeDropdown = () => {
        setTimeout(() => {
            dropdown.classList.remove('open');
            backdrop.style.display = 'none';
        }, 100); 
    }

    inputField.addEventListener('input', (e) => {
        let inputValue = inputField.value.toLowerCase();
        if (inputValue.length > 0) {
            dropdown.classList.add('open');
            inputField.style = "border-radius:15px 15px 0 0;"
            for (let j = 0; j < valueArray.length; j++) {
                if (valueArray[j].toLowerCase().indexOf(inputValue) === -1) {
                    dropdownArray[j].classList.add('closed');
                } else {
                    dropdownArray[j].classList.remove('closed');
                }
            }
        } else {
            for (let i = 0; i < dropdownArray.length; i++) {
                dropdownArray[i].classList.remove('closed');
            }
        }
    });

    // Click on Ticker Event
    dropdownArray.forEach(item => {
        item.addEventListener('click', async (evt) => {
            const ticker = item.getAttribute('data-value');
            await setDataframe(ticker);

            inputField.value = item.textContent;
            dropdownArray.forEach(dropdown => {
                dropdown.classList.add('closed');
            });

            // Fix chart scaling 
            document.getElementById('valuation').style.display = ''; 
            document.getElementById('financial-report').style.display = 'none';
            
            await Promise.all([
                getBusinessInfo(ticker),
                getTickerVisualization(ticker),
                generateRateTableComponent(),
                generateBalanceSheet(),
                generateOperationResult()
            ]);

            document.getElementById('valuation').scrollIntoView();
            // Save ticker name to session
            sessionStorage.setItem('selectedTicker', ticker);
        });
    })

    inputField.addEventListener('focus', () => {
        inputField.placeholder = 'Gõ để lọc cổ phiếu...';
        inputField.style = "border-radius:15px 15px 0 0;"
        dropdown.classList.add('open');
        dropdownArray.forEach(dropdown => {
            dropdown.classList.remove('closed');
        });
        backdrop.style.display = 'block';
    });

    inputField.addEventListener('blur', () => {
        inputField.style = "";
        inputField.placeholder = 'Chọn cổ phiếu';
        if (inputField.value.trim() !== "")
            inputField.style = "font-weight: 600;";
        closeDropdown();
    });
}


async function setDataframe(ticker){
    let content = {
        "ticker": ticker
    };
    const res = await fetch ('http://127.0.0.1:8000/read_all_csv/', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(content)
    })
}

async function updateCanslimDataPoint(numberOfPoints){
    let data = { 'data_point': numberOfPoints };
    try {
        const response = await fetch('http://127.0.0.1:8000/update_canslim_point/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        const res = await response.json();
        let chartElement = document.getElementById('chart-visualization');
        let canslimChart = chartElement.querySelectorAll(':scope > div')[1].querySelectorAll(':scope > div')[1];
        Plotly.react(canslimChart, [{
            x: res.update_dates,
            y: res.update_canslim_scores,
            line: {
                color: '#1f77b4',
                width: 3
            },
            name: '',
            hovertemplate: '<b>%{customdata}</b><br><i>Điểm</i>: %{y:.2f}',
            customdata: res.custom_data
        }], {
            template: 'gridon',
            title: {
                text: '<b>Điểm Canslim</b>',
                y: 0.9,
                x: 0.5,
                xanchor: 'center',
                yanchor: 'top'
            },
            xaxis: {
                title: {
                    text: '<i>Thời gian</i>',
                    font: {
                        size: 11
                    }
                },
                type: 'category',
            },
            yaxis: {
                title: {
                    text: '<i>Giá trị</i>',
                    font: {
                        size: 11
                    }
                }
            },
            margin: {
                l: 110, 
                b: 110  
            },
            legend: {
                title: 'Legend'
            },
            hoverlabel: {
                bgcolor: "white",
                font: {
                    size: 12,
                    family: "Rockwell"
                }
            },
            hovermode: 'x unified'
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

async function updateMX4DataPoint(numberOfPoints){
    let data = { 'data_point': numberOfPoints };
    try {
        const response = await fetch('http://127.0.0.1:8000/update_mx4_point/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        const res = await response.json();
        let chartElement = document.getElementById('chart-visualization');
        let mx4Chart = chartElement.querySelectorAll(':scope > div')[2].querySelectorAll(':scope > div')[1];
        Plotly.react(mx4Chart, [{
            x: res.update_dates,
            y: res.update_mx4_point,
            line: {
                color: '#1f77b4',
                width: 3
            },
            name: '',
            hovertemplate: '<b>%{customdata}</b><br><i>Điểm</i>: %{y:.2f}',
            customdata: res.custom_data
        }], {
            template: 'gridon',
            title: {
                text: '<b>Điểm 4M</b>',
                y: 0.9,
                x: 0.5,
                xanchor: 'center',
                yanchor: 'top'
            },
            xaxis: {
                title: {
                    text: '<i>Thời gian</i>',
                    font: {
                        size: 11
                    }
                },
                type: 'category',
            },
            yaxis: {
                title: {
                    text: '<i>Giá trị</i>',
                    font: {
                        size: 11
                    }
                }
            },
            margin: {
                l: 110, 
                b: 110  
            },
            legend: {
                title: 'Legend'
            },
            hoverlabel: {
                bgcolor: "white",
                font: {
                    size: 12,
                    family: "Rockwell"
                }
            },
            hovermode: 'x unified'
        });
    } catch (error) {
        console.error('Error:', error);
    }
}
async function getBusinessInfo(ticker){
    try {
        const content = {'ticker': ticker};
        const response = await fetch('http://127.0.0.1:8000/get_business_info/',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(content)
        })
        const res = await response.json();
        const sections = [
            { content: res.about, selector: '.business-profile' },
            { content: res.history, selector: '.business-history' },
            { content: res.prospect, selector: '.business-prospect' }
        ];
        
        sections.forEach((section, index) => {
            const element = document.querySelector(section.selector);
            
            // Clear the innerHTML
            element.innerHTML = '';

            // Remove the read mode
            var readMode = element.nextSibling.cloneNode();
            element.nextSibling.remove();

            if (index === 0) {
                const pElement = document.createElement('p');
                pElement.innerHTML = section.content;
                element.append(pElement);
                element.parentElement.append(readMode);
            } else {
                element.innerHTML = section.content;
                element.parentElement.append(readMode);
            }
        });

        // Clear the content on first load
        var elements = document.querySelectorAll('[data-original-content]');
        elements.forEach(function(element) {
            element.setAttribute('data-original-content', '');
        });
        readMoreNLess();
    } catch (error){
        console.log('Error at getBusinessInfor()',error);
    }
}

async function getTickerVisualization(ticker){
    let data = { 'ticker': ticker };
    try {
        const response = await fetch('http://127.0.0.1:8000/get_ticker_chart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const res = await response.json();
        const container = document.getElementById('chart-visualization');
        let canslimDataPoint = 20;
        let mx4DataPoint = 10;
        container.innerHTML = '';

        for (let obj in res){
            if (obj === 'cs_max_data_point') {
                canslimDataPoint = res[obj];
                continue;
            } else if (obj === 'mx4_max_data_point'){
                mx4DataPoint = res[obj];
                continue;
            }
            container.innerHTML += res[obj];
        }
        const scripts = container.querySelectorAll('script');
        if (scripts) {
            for (let script of scripts){
                const scriptContent = script.textContent || script.innerText;
                new Function(scriptContent)();
            }
        }
        addDropdowns(canslimDataPoint, mx4DataPoint);
    } catch (error) {
        console.error('Error:', error);
    }
}

function initializeSelectInstance(selector, maxPoints, updateDataPointFunction) {
    return new Promise(resolve => {
        let selectInstance = new TomSelect(selector, {
            valueField: 'id',
            labelField: 'title',
            searchField: 'title',
            selectOnTab: true,
            addPrecedence: true,
            placeholder: "Chọn số điểm...",
            create: false,
            maxItems: 1,
            maxOptions: null,
            preload: true,
            load: function (query, callback) {
                if (this.loading > 1) {
                    callback();
                    return;
                }
                let options = [];
                for (let i = 1; i <= maxPoints; i++) {
                    options.push({id: i, title: `${i} điểm`});
                }
                callback(options);
                selectInstance.setValue(maxPoints);
            },
            onItemAdd: (value) => {
                updateDataPointFunction(parseInt(value, 10));
                this.blur();
            }
        });

        resolve(selectInstance);
    });
}

async function addDropdowns(csMaxPoints=20, mx4MaxPoints=10){
    let chartElement = document.getElementById('chart-visualization');

    for (let index = 1; index < 3; index++) {
        let inputId, labelText;
        let chart = chartElement.querySelectorAll(':scope > div')[index].querySelector(':scope > div');

        if (index == 1) {
            inputId = 'cs-select';
            labelText = 'Số điểm Canslim';
        } else {
            inputId = 'mx4-select';
            labelText = 'Số điểm 4M';
        }

        let divider = document.createElement('hr');
        divider.className = 'hr hr-blurry mt-3 mb-2';

        let selectDiv = document.createElement('div');
        selectDiv.innerHTML = `
            <label for='${inputId}' class="fw-semibold">${labelText}</label>
            <input id='${inputId}' class="form-control"/>
        `;
        selectDiv.style = 'display: flex; align-items: center;';
        chart.parentNode.insertBefore(divider, chart);
        chart.parentNode.insertBefore(selectDiv, chart);
    }
    
    Promise.all([
        initializeSelectInstance('#cs-select', csMaxPoints, updateCanslimDataPoint),
        initializeSelectInstance('#mx4-select', mx4MaxPoints, updateMX4DataPoint)
    ]).then(([csSelectInstance, mx4SelectInstance]) => {
        document.querySelectorAll('.ts-wrapper').forEach(element => {
            element.style = 'width: 24%; margin:20px 15px;';
        });
    });
}

function readMoreNLess() {
    const readMore = document.querySelectorAll('.read-more');
    
    readMore.forEach(element => {
        const contentId = element.getAttribute('data-content');
        const contentElement = document.querySelector('.' + contentId);

        // Store the original content in a data attribute, if it doesn't exist
        if (!contentElement.getAttribute('data-original-content')) {
            contentElement.setAttribute('data-original-content', contentElement.innerHTML);
        }

        const maxLength = 350;
        let originalContent = contentElement.getAttribute('data-original-content');
        
        // Check if the content exceeds the maximum length
        if (originalContent.length > maxLength) {
            let truncatedText = originalContent.slice(0, maxLength) + "...";
            contentElement.innerHTML = truncatedText;
            element.style.display = 'inline';
            element.innerText = 'Đọc Thêm';
        } else {
            element.style.display = 'none';
        }
        $(element).off('click', toggleReadMode);
        $(element).on('click', toggleReadMode);
        function toggleReadMode() {
            if (this.innerText === 'Đọc Thêm') {
                contentElement.innerHTML = originalContent;
                this.innerText = 'Thu Gọn';
            } else {
                let truncatedText = originalContent.slice(0, maxLength) + "...";
                contentElement.innerHTML = truncatedText;
                this.innerText = 'Đọc Thêm';
            }
        }
    });
}

function onValuationClick() {
    const valuationNav = document.getElementById('valuation-nav-btn');
    valuationNav.addEventListener('click', () => {

        const selectedTicker = sessionStorage.getItem('selectedTicker');
        const inputElement = document.querySelector('.chosen-value');

        if (!selectedTicker) {
            setTimeout(() => {
                inputElement.focus();
            }, 100);
        } else {
            // getTickerVisualization(selectedTicker);
            const textValue = document.querySelector(`[data-value="${selectedTicker}"`).innerText;
            inputElement.value = textValue;
            document.getElementById('financial-report').style.display = 'none';
            document.getElementById('valuation').style.display = '';
        }
    });
}

function get_financial_report() {
    const financialBtn = document.getElementById('financial-nav-btn');
    financialBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const inputElement = document.querySelector('.chosen-value');
        const valuation = document.getElementById('valuation');

        valuation.style.display = 'none';
        inputElement.value = '';
        const financialContainer = document.getElementById('financial-report');
        financialContainer.style.display = '';
        const response = await fetch('http://127.0.0.1:8000/get_financial_report/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data) {
            document.getElementById('eps-chart-container').innerHTML = data.graph_html_eps;
            document.getElementById('lnst-chart-container').innerHTML = data.graph_html_lnst;
            document.getElementById('fed-chart-container').innerHTML = data.graph_html_fed;
        }   
        const scripts = financialContainer.querySelectorAll('script');
        if (scripts) {
            for (let script of scripts){
                const scriptContent = script.textContent || script.innerText;
                new Function(scriptContent)();
            }
        }
        financialContainer.scrollIntoView();
    });
}

function scrollToTop() {
    var btn = document.getElementById('btn-back-to-top');
    btn.addEventListener('click', () => {
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
    });
}
window.onscroll = function () {
    var btnScrollToTop = document.getElementById('btn-back-to-top');
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        btnScrollToTop.style.display = "block";
    } else {
        btnScrollToTop.style.display = "none";
    }
};

document.addEventListener('DOMContentLoaded', function () {
    sessionStorage.setItem('selectedTicker', '')
    get_financial_report();
    onValuationClick();
    inputHandler();
    scrollToTop();
});
