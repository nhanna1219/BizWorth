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
            
            inputField.value = item.textContent;
            dropdownArray.forEach(dropdown => {
                dropdown.classList.add('closed');
            });
            await getTickerVisualization(ticker);
            document.getElementById('valuation').scrollIntoView();
        });
    })

    inputField.addEventListener('focus', () => {
        inputField.placeholder = 'Type to filter...';
        inputField.style = "border-radius:15px 15px 0 0;"
        dropdown.classList.add('open');
        dropdownArray.forEach(dropdown => {
            dropdown.classList.remove('closed');
        });
        backdrop.style.display = 'block';
    });

    inputField.addEventListener('blur', () => {
        inputField.style = "";
        inputField.placeholder = 'Choose Your Ticker';
        if (inputField.value.trim() !== "")
            inputField.style = "font-weight: 600;";
        closeDropdown();
    });
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
        container.innerHTML = '';
        for (let obj in res){
            container.innerHTML += res[obj];
        }
        // container.innerHTML = res.graph_stock_pred;
        const scripts = container.querySelectorAll('script');
        if (scripts) {
            for (let script of scripts){
                const scriptContent = script.textContent || script.innerText;
                new Function(scriptContent)();
            }
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
document.addEventListener('DOMContentLoaded', function () {
    inputHandler();

});
