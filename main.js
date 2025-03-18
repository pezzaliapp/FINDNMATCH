// Funzione per leggere un file Excel e restituire un array di array
function readExcel(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = function(e) {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const json = XLSX.utils.sheet_to_json(sheet, { header: 1 });
      resolve(json);
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

// Funzione per confrontare le corrispondenze
async function compareMatches() {
  const file1 = document.getElementById("file1").files[0];
  const file2 = document.getElementById("file2").files[0];
  const col1 = parseInt(document.getElementById("col1").value) - 1;
  const col2 = parseInt(document.getElementById("col2").value) - 1;

  if (!file1 || !file2) {
    alert("Seleziona entrambi i file Excel.");
    return;
  }
  if (isNaN(col1) || isNaN(col2)) {
    alert("Inserisci numeri validi per le colonne.");
    return;
  }

  try {
    const dataArray1 = await readExcel(file1);
    const dataArray2 = await readExcel(file2);

    const column1Values = dataArray1.map(row => row[col1]);
    const column2Values = dataArray2.map(row => row[col2]);

    // Trova le corrispondenze (valori comuni)
    const matches = column1Values.filter(value => column2Values.includes(value));

    if (matches.length > 0) {
      alert("Trovate " + matches.length + " corrispondenze!");
      generateExcel("corrispondenze", matches);
    } else {
      alert("Nessuna corrispondenza trovata.");
    }
  } catch (error) {
    alert("Errore nella lettura dei file: " + error);
  }
}

// Funzione per confrontare le differenze
async function compareDifferences() {
  const file1 = document.getElementById("file1").files[0];
  const file2 = document.getElementById("file2").files[0];
  const col1 = parseInt(document.getElementById("col1").value) - 1;
  const col2 = parseInt(document.getElementById("col2").value) - 1;

  if (!file1 || !file2) {
    alert("Seleziona entrambi i file Excel.");
    return;
  }
  if (isNaN(col1) || isNaN(col2)) {
    alert("Inserisci numeri validi per le colonne.");
    return;
  }

  try {
    const dataArray1 = await readExcel(file1);
    const dataArray2 = await readExcel(file2);

    const column1Values = dataArray1.map(row => row[col1]);
    const column2Values = dataArray2.map(row => row[col2]);

    // Calcola le differenze:
    // Valori presenti in file1 ma non in file2
    const missingInFile2 = column1Values.filter(value => !column2Values.includes(value));
    // Valori presenti in file2 ma non in file1
    const missingInFile1 = column2Values.filter(value => !column1Values.includes(value));

    let differences = {
      "Presenti in File 1 ma non in File 2": missingInFile2,
      "Presenti in File 2 ma non in File 1": missingInFile1
    };

    // Mostra il risultato (puoi usare alert o aggiornare il DOM)
    let msg = "";
    msg += "Differenze:\n";
    msg += "File 1 > File 2: " + missingInFile2.length + " valori\n";
    msg += "File 2 > File 1: " + missingInFile1.length + " valori\n";

    alert(msg);
    // Genera file Excel con le differenze
    generateExcelDifferences(differences);
  } catch (error) {
    alert("Errore nella lettura dei file: " + error);
  }
}

// Funzione per generare e scaricare un file Excel per le corrispondenze
function generateExcel(type, data) {
  const wsData = [[type === "corrispondenze" ? "Valori Corrispondenti" : ""]];
  data.forEach(val => {
    wsData.push([val]);
  });
  const ws = XLSX.utils.aoa_to_sheet(wsData);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, type);
  XLSX.writeFile(wb, type + "_result.xlsx");
}

// Funzione per generare e scaricare un file Excel per le differenze
function generateExcelDifferences(differences) {
  let wsData = [];
  // Aggiungi una sezione per le differenze di File 1 rispetto a File 2
  wsData.push(["Valori presenti in File 1 ma non in File 2"]);
  differences["Presenti in File 1 ma non in File 2"].forEach(val => {
    wsData.push([val]);
  });
  wsData.push([]); // Riga vuota per separare le sezioni
  wsData.push(["Valori presenti in File 2 ma non in File 1"]);
  differences["Presenti in File 2 ma non in File 1"].forEach(val => {
    wsData.push([val]);
  });
  
  const ws = XLSX.utils.aoa_to_sheet(wsData);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Differenze");
  XLSX.writeFile(wb, "differenze_result.xlsx");
}

// Event listeners per i pulsanti
document.getElementById("compareButton").addEventListener("click", compareMatches);
document.getElementById("differenceButton").addEventListener("click", compareDifferences);