#!/usr/bin/env python3

class TicketSalesCalculator:
    def __init__(self, desired_total_value, total_participants, cost_per_participant,
                 non_paying_lower, non_paying_upper,
                 tiers, allocation_percentages, first_batch_total, num_batches):
        """
        Initialize with:
          - desired_total_value: The desired total dollar value (target revenue).
          - total_participants: Total number of participants (e.g., 80,000).
          - cost_per_participant: Cost per participant (e.g., 750).
            (This is the cost for every participant, though revenue comes only from paying ones.)
          - non_paying_lower, non_paying_upper: Bounds for non-paying participants.
            (Midpoint is computed automatically.)
          - tiers: List of ticket prices (e.g., [550, 750, 1000, 1250]).
          - allocation_percentages: Planned percentage allocations for each tier (should sum to 100).
          - first_batch_total: Total tickets planned for the first batch.
          - num_batches: Total number of batches planned.
        """
        self.desired_total_value = desired_total_value
        self.total_participants = total_participants
        self.cost_per_participant = cost_per_participant

        # Non-paying participants:
        self.non_paying_lower = non_paying_lower
        self.non_paying_upper = non_paying_upper
        self.non_paying_mid = (non_paying_lower + non_paying_upper) / 2

        # Calculate paying participants for each scenario:
        # (Fewer non-payers => more paying participants.)
        self.paying_best = self.total_participants - self.non_paying_upper   # best-case: many pay
        self.paying_mid = self.total_participants - self.non_paying_mid        # midpoint scenario
        self.paying_worst = self.total_participants - self.non_paying_lower     # worst-case: fewer pay

        # Compute revenue target based on paying participants (using midpoint scenario by default)
        self.revenue_target = self.paying_mid * self.cost_per_participant

        # Ticket tiers:
        self.tiers = tiers  # e.g., [550, 750, 1000, 1250]
        # Allocation percentages (should sum to 100)
        self.allocation_percentages = allocation_percentages

        # Batch planning:
        self.first_batch_total = first_batch_total  # e.g., 20000 for first batch
        self.num_batches = num_batches
        self.global_ticket_cap = self.first_batch_total * self.num_batches

        # For the first batch, compute initial planned allocations (absolute numbers)
        self.current_batch_planned_allocations = [
            int((pct / 100) * self.first_batch_total) for pct in self.allocation_percentages
        ]

        # Initialize storage for batches, cumulative sales, etc.
        self.batches = []  # Each batch is stored as a dict with 'sales' and 'batch_revenue'
        self.cumulative_revenue = 0
        self.cumulative_sales = [0] * len(tiers)
        # For dynamic adjustment, store last batch's sales (initialize to zeros)
        self.last_batch_sales = [0] * len(tiers)

        # Social engineering adjustment factors:
        self.increase_factor = 0.2  # for extra sales in higher tiers (Tier 3 & 4)
        self.reduction_factor = 0.2  # for excess sales in Tier 2

    def print_scenario_analysis(self):
        print("\n--- Event Cost & Revenue Scenario Analysis ---")
        print(f"Desired Total Dollar Value: ${self.desired_total_value:,}")
        print(f"Total Participants: {self.total_participants}")
        print(f"Cost per Participant: ${self.cost_per_participant}")
        print("\nNon-Paying Participants Range:")
        print(f"  Lower Bound: {self.non_paying_lower}")
        print(f"  Upper Bound: {self.non_paying_upper}")
        print(f"  (Computed Midpoint: {self.non_paying_mid})")
        print("\nCalculated Paying Participants:")
        print(f"  Best-case (few non-payers): {self.paying_best}")
        print(f"  Midpoint: {self.paying_mid}")
        print(f"  Worst-case (many non-payers): {self.paying_worst}")
        print("\nRevenue Target (using midpoint paying participants):")
        print(f"  ${self.revenue_target:,}")
        print(f"\nGlobal Ticket Cap (Total tickets to be sold across batches): {self.global_ticket_cap}")
        print(f"Number of Batches: {self.num_batches}")
        print(f"First Batch Total Tickets: {self.first_batch_total}")
        print("\nInitial Batch Allocations (absolute numbers) per tier:")
        for i, alloc in enumerate(self.current_batch_planned_allocations):
            print(f"  Tier {i+1} (${self.tiers[i]}): {alloc} tickets (from {self.allocation_percentages[i]}% input)")

    def add_batch(self, sales):
        """
        Record a batch of sales (absolute numbers per tier).
        Updates cumulative revenue and sales.
        Also, stores the last batch's sales for dynamic adjustments.
        """
        batch_revenue = sum(sales[i] * self.tiers[i] for i in range(len(self.tiers)))
        self.cumulative_revenue += batch_revenue
        for i in range(len(sales)):
            self.cumulative_sales[i] += sales[i]
        self.batches.append({'sales': sales, 'batch_revenue': batch_revenue})
        self.last_batch_sales = sales  # store for dynamic adjustments
        print(f"\nBatch added with revenue: ${batch_revenue:,.2f}")

    def remaining_revenue(self):
        return self.revenue_target - self.cumulative_revenue

    def remaining_tickets_global(self):
        # Global remaining tickets is the global cap minus cumulative sales across batches
        return self.global_ticket_cap - sum(self.cumulative_sales)

    def print_report(self):
        print("\n--- Sales Report ---")
        print(f"Revenue Target: ${self.revenue_target:,}")
        print(f"Cumulative Revenue: ${self.cumulative_revenue:,.2f}")
        print(f"Remaining Revenue: ${self.remaining_revenue():,.2f}")
        baseline_needed = self.remaining_revenue() / self.cost_per_participant if self.cost_per_participant else 0
        print(f"Baseline Tickets Needed (at ${self.cost_per_participant}): {baseline_needed:.0f}")
        print("\nCumulative Sales by Tier:")
        for i, sales in enumerate(self.cumulative_sales):
            print(f"  Tier {i+1} (${self.tiers[i]}): {sales} tickets sold")
        print(f"\nBatch Details:")
        for idx, batch in enumerate(self.batches):
            print(f"  Batch {idx+1}: Sales: {batch['sales']}, Revenue: ${batch['batch_revenue']:,.2f}")
        print(f"\nGlobal Remaining Tickets: {self.remaining_tickets_global()}")

    def dynamic_allocation_suggestion(self):
        """
        Suggests the number of tickets to allocate in the next batch and computes new weight percentages.
        The suggestion is based on:
          - The remaining global ticket pool.
          - The base planned allocations for the next batch (from the original percentages).
          - Dynamic adjustments (rollover from previous batch and oversell/undersell adjustments).
          - A check on the required weighted average to meet revenue goals.
        """
        print("\n--- Dynamic Allocation Suggestions ---")
        remaining_global = self.remaining_tickets_global()
        # Planned total for next batch is the lesser of first_batch_total and remaining global tickets.
        next_batch_total = min(self.first_batch_total, remaining_global)
        # Base planned allocations for next batch from original percentages:
        base_planned = [ (pct / 100) * next_batch_total for pct in self.allocation_percentages ]
        
        # Compute rollover from the last batch:
        # Rollover per tier = (last batch planned allocation) - (last batch sales), capped at 0.
        rollover = [ max(0, self.current_batch_planned_allocations[i] - self.last_batch_sales[i])
                     for i in range(len(self.tiers)) ]
        
        # Dynamic adjustment for Tier 1:
        extra_tier2 = max(0, self.last_batch_sales[1] - self.current_batch_planned_allocations[1])
        reduction_adjustment = int(extra_tier2 * self.reduction_factor)
        extra_tier3 = max(0, self.last_batch_sales[2] - self.current_batch_planned_allocations[2])
        extra_tier4 = max(0, self.last_batch_sales[3] - self.current_batch_planned_allocations[3])
        increase_adjustment = int((extra_tier3 + extra_tier4) * self.increase_factor)
        net_adjustment = increase_adjustment - reduction_adjustment
        
        suggested_allocations = [0] * len(self.tiers)
        suggested_allocations[0] = max(0, base_planned[0] + net_adjustment)
        for i in range(1, len(self.tiers)):
            suggested_allocations[i] = base_planned[i] + rollover[i]
        
        total_suggested = sum(suggested_allocations)
        if total_suggested > next_batch_total:
            scaling_factor = next_batch_total / total_suggested
            suggested_allocations = [ alloc * scaling_factor for alloc in suggested_allocations ]
            total_suggested = next_batch_total
        
        # Check required average price for the next batch:
        required_avg = self.remaining_revenue() / next_batch_total if next_batch_total else 0
        if required_avg > self.tiers[0]:
            print(f"\nRequired average for next batch is ${required_avg:.2f}, which is above Tier 1 price ${self.tiers[0]:.2f}.")
            print("Cutting off Tier 1 in the next batch to help meet revenue targets.")
            suggested_allocations[0] = 0
            other_total = sum(suggested_allocations[1:])
            if other_total > 0:
                scale = next_batch_total / other_total
                for i in range(1, len(suggested_allocations)):
                    suggested_allocations[i] *= scale
                total_suggested = next_batch_total
        
        new_percentages = [ (alloc / total_suggested) * 100 if total_suggested else 0 for alloc in suggested_allocations ]
        
        print(f"\nNext batch total planned tickets: {next_batch_total}")
        print(f"Base planned allocations (from percentages): {['{:.0f}'.format(x) for x in base_planned]}")
        print(f"Rollover from last batch: {['{:.0f}'.format(x) for x in rollover]}")
        print(f"Tier 2 extra sales: {extra_tier2} -> Reduction: {reduction_adjustment} tickets")
        print(f"Tiers 3 & 4 extra sales: {extra_tier3 + extra_tier4} -> Increase: {increase_adjustment} tickets")
        print(f"Net adjustment for Tier 1: {net_adjustment} tickets")
        print("\nSuggested next batch allocations (absolute numbers):")
        for i, alloc in enumerate(suggested_allocations):
            print(f"  Tier {i+1} (${self.tiers[i]}): {alloc:.0f} tickets")
        print("\nNew weight percentages for next batch:")
        for i, pct in enumerate(new_percentages):
            print(f"  Tier {i+1}: {pct:.1f}%")
        print("\nAdjust your next batch based on these suggestions.\n")
        
        self.current_batch_planned_allocations = [ int(round(x)) for x in suggested_allocations ]
    
def main():
    print("Ticket Sales Dynamic Allocation Calculator\n")
    
    # Basic event inputs:
    desired_total_value = float(input("Enter desired total dollar value (e.g., 60000000): "))
    total_participants = int(input("Enter total participants (e.g., 80000): "))
    cost_per_participant = float(input("Enter cost per participant (e.g., 750): "))
    
    print("\nEnter non-paying participants (as a range):")
    non_paying_lower = int(input("  Lower Bound (e.g., 10000): "))
    non_paying_upper = int(input("  Upper Bound (e.g., 20000): "))
    
    # Ticket pricing tiers:
    print("\nEnter ticket prices for 4 tiers:")
    tiers = []
    for i in range(4):
        price = float(input(f"  Tier {i+1} price: "))
        tiers.append(price)
    
    # Enter allocation percentages (should sum to 100):
    print("\nEnter planned allocation percentages for each tier (should sum to 100):")
    allocation_percentages = []
    for i in range(4):
        pct = float(input(f"  Tier {i+1} allocation percentage: "))
        allocation_percentages.append(pct)
    
    # Batch parameters:
    first_batch_total = int(input("\nEnter total tickets planned for the first batch: "))
    num_batches = int(input("Enter total number of batches: "))
    
    # Create the TicketSalesCalculator instance:
    calculator = TicketSalesCalculator(desired_total_value, total_participants, cost_per_participant,
                                         non_paying_lower, non_paying_upper,
                                         tiers, allocation_percentages, first_batch_total, num_batches)
    
    # Show scenario analysis:
    calculator.print_scenario_analysis()
    
    batch_count = 0
    while batch_count < calculator.num_batches:
        print(f"\n--- Batch Entry ({batch_count+1} of {calculator.num_batches}) ---")
        sales = []
        for i in range(4):
            s = int(input(f"Enter tickets sold for Tier {i+1} (${tiers[i]}): "))
            sales.append(s)
        
        calculator.add_batch(sales)
        calculator.print_report()
        if batch_count < calculator.num_batches - 1:
            calculator.dynamic_allocation_suggestion()
        batch_count += 1
        if batch_count >= calculator.num_batches:
            print("\nReached the specified total number of batches.")
            break
        
        # Prompt user and validate input:
        valid_response = False
        while not valid_response:
            cont = input("Add another batch? (y/n): ").strip().lower()
            if cont in ['y', 'n']:
                valid_response = True
            else:
                print("Please enter 'y' for yes or 'n' for no.")
        if cont == 'n':
            break
    
    print("\nFinal Report:")
    calculator.print_report()

if __name__ == "__main__":
    main()