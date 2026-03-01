document.addEventListener("DOMContentLoaded", async () => {
    // 1. Fetch updated options (Splits, Equipment, Volumes)
    try {
        const response = await fetch("/options");
        const data = await response.json();

        // Populate Workout Modes (Splits + Single Sessions)
        const splitSelect = document.getElementById("splitName");
        data.splits.forEach(split => {
            const option = document.createElement("option");
            option.value = split;
            option.textContent = split;
            splitSelect.appendChild(option);
        });

        // Populate Volume Levels
        const volumeSelect = document.getElementById("volumeLevel");
        data.volumes.forEach(vol => {
            const option = document.createElement("option");
            option.value = vol;
            option.textContent = vol;
            if(vol === "Normal") option.selected = true;
            volumeSelect.appendChild(option);
        });

        // Populate Equipment Checkboxes
        const equipmentList = document.getElementById("equipmentList");
        data.equipment.forEach(eq => {
            const div = document.createElement("div");
            div.innerHTML = `
                <input type="checkbox" id="eq_${eq}" value="${eq}" checked>
                <label for="eq_${eq}">${eq}</label>
            `;
            equipmentList.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading options:", error);
    }

    // 2. Generate Plan Button Click
    document.getElementById("generateBtn").addEventListener("click", async () => {
        const splitName = document.getElementById("splitName").value;
        const volumeLevel = document.getElementById("volumeLevel").value;
        const checkedEquipments = Array.from(document.querySelectorAll('#equipmentList input:checked'))
                                     .map(cb => cb.value);

        if (checkedEquipments.length === 0) {
            alert("Please select at least one equipment!");
            return;
        }

        const requestData = {
            split_name: splitName,
            equipment_list: checkedEquipments,
            volume_level: volumeLevel
        };

        try {
            const response = await fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestData)
            });

            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = ""; // Clear previous results

            if (!response.ok) {
                resultsDiv.innerHTML = `<p style="color: red;">No exercises found for these criteria.</p>`;
                return;
            }

            const weeklyPlan = await response.json();

            // 3. Render Weekly Plan as Cards
            for (const [day, exercises] of Object.entries(weeklyPlan)) {
                const dayCard = document.createElement("div");
                dayCard.className = "day-card";

                let html = `<h3>${day}</h3>`;

                if (typeof exercises === "string") {
                    // It's a Rest Day message
                    html += `<p class="rest-msg">${exercises}</p>`;
                } else {
                   // It's an exercise list
                    html += `<table>
                                <tr>
                                    <th>Exercise</th>
                                    <th>Target</th> <th>Sets/Reps</th>
                                    <th>Tool</th>
                                </tr>`;
                    exercises.forEach(ex => {
                        html += `<tr>
                                    <td>${ex.name}</td>
                                    <td style="color: #b3b3b3; font-size: 0.9rem;">${ex.target}</td> <td><strong>${ex.volume}</strong></td>
                                    <td>${ex.equipment}</td>
                                 </tr>`;
                    });
                    html += `</table>`;
                }

                dayCard.innerHTML = html;
                resultsDiv.appendChild(dayCard);
            }

        } catch (error) {
            console.error("Error generating plan:", error);
        }
    });
});