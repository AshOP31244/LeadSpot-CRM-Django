const leads = [
  { id: "CMP-001", company: "Reliance", client: "Piyush", phone: "9876543210" },
  { id: "CMP-002", company: "Tata", client: "Rahul", phone: "9123456789" }
];

const tbody = document.getElementById("leads-table-body");

leads.forEach(l => {
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>${l.id}</td>
    <td>${l.company}</td>
    <td>${l.client}</td>
    <td>${l.phone}</td>
  `;
  tr.onclick = () => window.location.href = `/lead/${l.id.replace(/\D/g,'') || 1}/`;
  tbody.appendChild(tr);
});
