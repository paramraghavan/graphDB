# What is choose doing in the query below

It's functioning like a if/else, case/when

- When value for variable,<OLIN_variable>, is 'FNA'
    - then do not apply filter show all the order line item details for the customers latest order

- When value for variable,<OLIN_variable>, is other than 'FNA'
    - then do not apply filter, do not show all the order line item details, but filter by order line item whose value
      is passed in the variable order line item number, <OLIN_variable>,  for the customers latest order

```gremlin
g.V().hasLabel('customer').has('customer_id', 'customer id value')
.outE().hasLabel('to-order').inV()
.hasLabel('order').order().by('order_number', desc)
.limit(1)
.outE().inV()
.choose(
// if value matches 'NA', filter not applicable, do not apply filter  by orer line item number
  __.constant(<OLIN_variable>).is('FNA'), 
  __.filter(
    __.or(
      __.hasLabel('order-line-item')
    )
  ), //else
  __.filter(
  __.hasLabel('order-line-item').has('order_line_item_number, <OLIN_variable>))
)
.repeat(
  outE().inV()
  .or(
    hasLabel('order_line_item_details'),
    hasLabel('order-line-item-ship-status'),
    hasLabel('customer-delivery-status')
  ).simplePath()
)
.emit().path().unfold()
```