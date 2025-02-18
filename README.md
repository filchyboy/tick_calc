# Ticket Sales Calculator

A Python-based calculator for managing tiered ticket sales across multiple batches, with dynamic allocation adjustments and revenue tracking. This is a simplified example of yield management techniques for event organizers.

## Overview

This tool helps event organizers manage ticket sales by:
- Calculating optimal ticket allocations across different price tiers
- Tracking sales and revenue across multiple batches
- Dynamically adjusting allocations based on previous batch performance
- Providing scenario analysis for different participant payment rates

## Features

- Multiple pricing tiers support
- Batch-based sales management
- Dynamic allocation adjustments based on sales patterns
- Revenue target tracking
- Non-paying participant scenario analysis
- Automatic reallocation suggestions for optimal revenue
- Comprehensive reporting capabilities

## Usage

```python
calculator = TicketSalesCalculator(
    desired_total_value=1000000,      # Target revenue
    total_participants=80000,          # Total expected participants
    cost_per_participant=750,          # Cost per participant
    non_paying_lower=20000,           # Minimum non-paying participants
    non_paying_upper=30000,           # Maximum non-paying participants
    tiers=[550, 750, 1000, 1250],     # Ticket price tiers
    allocation_percentages=[40, 30, 20, 10],  # Percentage allocation per tier
    first_batch_total=20000,          # Number of tickets in first batch
    num_batches=4                      # Total number of planned batches
)

# Print initial analysis
calculator.print_scenario_analysis()

# Add batch sales
calculator.add_batch([8000, 6000, 4000, 2000])

# Get suggestions for next batch
calculator.dynamic_allocation_suggestion()

# View current status
calculator.print_report()
```

## Key Components

- **Scenario Analysis**: Calculates different scenarios based on varying numbers of paying vs non-paying participants
- **Revenue Tracking**: Monitors progress toward revenue targets
- **Dynamic Adjustments**: Automatically suggests allocation adjustments based on:
  - Previous batch performance
  - Remaining revenue targets
  - Global ticket caps
  - Tier-specific sales patterns

## Installation

No external dependencies required. Simply clone the repository and import the `TicketSalesCalculator` class from `tick_calc.py`.

## License

MIT License

Copyright (c) 2025 Christopher Filkins
