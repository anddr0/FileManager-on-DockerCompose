const SERVER_ADDRESS = window.location.hostname;
let files = [];

function renderFiles() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    files.forEach(file => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${file.id}</td>
            <td>${file.name}</td>
            <td class="actions">
                <i class="fas fa-download" onclick="downloadFile(${file.id})"></i>
                <i class="fas fa-edit" onclick="editFile(${file.id})"></i>
                <i class="fas fa-trash" onclick="deleteFile(${file.id})"></i>
            </td>
        `;
        fileList.appendChild(row);
    });
}

async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const customFileName = document.getElementById('fileName').value;
    if (fileInput.files.length === 0) {
        alert('Please select a file');
        return;
    }
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('customName', customFileName);

    try {
        const response = await fetch(`http://${SERVER_ADDRESS}:5000/upload`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        files.push(data);
        renderFiles();
        fileInput.value = '';
        document.getElementById('fileName').value = '';
    } catch (error) {
        console.error('Error:', error);
    }
}

async function downloadFile(id) {
    try {
        const response = await fetch(`http://${SERVER_ADDRESS}:5000/download/${id}`);
        const data = await response.json();
        const url = data.url;
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = files.find(file => file.id === id).name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error:', error);
    }
}

async function editFile(id) {
    const newName = prompt('Enter new file name:');
    if (newName) {
        const formData = new FormData();
        formData.append('name', newName);
        
        try {
            const response = await fetch(`http://${SERVER_ADDRESS}:5000/rename/${id}`, {
                method: 'PUT',
                body: formData
            });
            const data = await response.json();
            const file = files.find(f => f.id === id);
            file.name = data.name;
            renderFiles();
        } catch (error) {
            console.error('Error:', error);
        }
    }
}

async function deleteFile(id) {
    try {
        const response = await fetch(`http://${SERVER_ADDRESS}:5000/delete/${id}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        files = files.filter(file => file.id !== id);
        renderFiles();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function getFiles() {
    try {
        const response = await fetch(`http://${SERVER_ADDRESS}:5000/get_files`);
        const data = await response.json();
        files = data;
        renderFiles();
    } catch (error) {
        console.error('Error:', error);
    }
}

// Initial fetch of files from the backend
getFiles();
