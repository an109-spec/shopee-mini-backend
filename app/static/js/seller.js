document.addEventListener("DOMContentLoaded", () => {

    const chartElement = document.getElementById("revenueChart");

    if(!chartElement) return;

    const ctx = chartElement.getContext("2d");

    fetch("/seller/api/revenue")
        .then(res => res.json())
        .then(data => {

            new Chart(ctx, {
                type: "line",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Doanh thu",
                        data: data.values,
                        borderWidth: 2,
                        tension: 0.4
                    }]
                }
            });

        });

});