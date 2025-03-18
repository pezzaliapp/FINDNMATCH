document.getElementById("compareButton").addEventListener("click", function() {
    const file1 = document.querySelector('input[name="file1"]').files[0];
    const file2 = document.querySelector('input[name="file2"]').files[0];
    const col1 = parseInt(document.querySelector('input[name="col1"]').value) - 1;
    const col2 = parseInt(document.querySelector('input[name="col2"]').value) - 1;

    if (!file1 || !file2) {
        alert("Seleziona entrambi i file.");
        return;
    }

    const reader1 = new FileReader();
    const reader2 = new FileReader();

    reader1.onload = function(e) {
        const data1 = new Uint8Array(e.target.result);
        const workbook1 = XLSX.read(data1, {type: 'array'});
        const sheet1 = workbook1.Sheets[workbook1.SheetNames[0]];
        const dataArray1 = XLSX.utils.sheet_to_json(sheet1, {header: 1});

        reader2.onload = function(e) {
            const data2 = new Uint8Array(e.target.result);
            const workbook2 = XLSX.read(data2, {type: 'array'});
            const sheet2 = workbook2.Sheets[workbook2.SheetNames[0]];
            const dataArray2 = XLSX.utils.sheet_to_json(sheet2, {header: 1});

            // Creiamo array con i valori delle colonne selezionate
            const column1Values = dataArray1.map(row => row[col1]);
            const column2Values = dataArray2.map(row => row[col2]);

            // Troviamo le corrispondenze
            const matches = column1Values.filter(value => column2Values.includes(value));
            
            if (matches.length > 0) {
                alert("Trovate " + matches.length + " corrispondenze!");
            } else {
                alert("Nessuna corrispondenza trovata.");
            }
        };
        reader2.readAsArrayBuffer(file2);
    };
    reader1.readAsArrayBuffer(file1);
});