document.getElementById('queryForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const query = document.getElementById('queryInput').value;
    fetch('/query', {
        method: 'POST',
        body: new URLSearchParams('query=' + query)
    })
    .then(response => response.json())
    .then(data => {
        // Use D3.js to render the graph
        // data contains the vertices and edges
        console.log(data)
    })
    .catch(error => console.error('Error:', error));
});
