document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');

    form.addEventListener('submit', function (e) {
        e.preventDefault(); 

        const taskName = document.getElementById('task-name').value;
        const scanConfig = document.getElementById('scan-config').value;
        const targetHost = document.getElementById('target-host').value;
        const startImmediately = document.querySelector('input[name="schedule"]:checked').value === "immediately";
        const scheduleDate = document.getElementById('schedule-date').value;
        const scheduleTime = document.getElementById('schedule-time').value;
        const emailReport = document.getElementById('email-report').value;

        const taskData = {
            name: taskName,
            scanConfig: scanConfig,
            targetHost: targetHost,
            date: startImmediately ? new Date().toISOString().split('T')[0] : scheduleDate,
            time: startImmediately ? new Date().toISOString().split('T')[1].slice(0, 5) : scheduleTime,
            emailReport: emailReport
        };

   
        fetch('/add_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData), 
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('Task added successfully!');
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        
    });
});
document.addEventListener('DOMContentLoaded', () => {
    
    fetch('/get_port_lists')
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            console.log('Port Lists:', data.port_lists);
            
            const portListSelect = document.getElementById('target-host');
            data.port_lists.forEach(portList => {
                const option = document.createElement('option');
                option.value = portList.uuid;
                option.textContent = portList.name;
                portListSelect.appendChild(option);
            });
        } else {
            console.error('Error fetching port lists:', data.message);
        }
    })
    .catch(error => console.error('Error:', error));
});

