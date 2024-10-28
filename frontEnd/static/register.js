document.addEventListener("DOMContentLoaded", () => {
    fetchCVEData();
});


function updateContent(section) {
    window.location.href = section;
}


function fetchCVEData() {
    fetch('/get_latest_reports')
        .then(response => response.json())
        .then(data => {
            populateCVETable(data);
        })
        .catch(error => {
            console.error('Error fetching CVE data:', error);
        });
}

function populateCVETable(data) {
    const tableBody = document.querySelector('#cve-table tbody');
    tableBody.innerHTML = ''; 

    data.forEach(report => {
        report.CVEs.forEach(cve => {
            const row = document.createElement('tr');

            const cveIDCell = document.createElement('td');
            cveIDCell.textContent = cve['CVE ID'];

            const severityCell = document.createElement('td');
            severityCell.textContent = cve['Severity'];

            const descriptionCell = document.createElement('td');
            descriptionCell.textContent = cve['Description'];

            row.appendChild(cveIDCell);
            row.appendChild(severityCell);
            row.appendChild(descriptionCell);

            tableBody.appendChild(row);
        });
    });
}
