<template>
<skeleton theme="opacity" style="width:200px" shape="radius" bg-color="#dcdbdc">
    <row>
      <col :span="8">
        <tb-skeleton :aspect-ratio="1" shape="circle">
        </tb-skeleton>
      <col :span="16">
        <row>
          <col :span="12" style="padding-left: 10px;margin-top: 5px">
            <tb-skeleton :aspect-ratio="0.2"></tb-skeleton>
          <col :span="24" style="padding-left: 10px;margin-top: 10px">
            <tb-skeleton :aspect-ratio="0.1"></tb-skeleton>
          <col :span="24" style="padding-left: 10px;margin-top: 10px">
            <tb-skeleton :aspect-ratio="0.1"></tb-skeleton>
        </row>
    </row>
  </skeleton>
</template>

<script>
import { TbSkeleton, Skeleton } from 'tb-skeleton'

export default {
  components: {
    TbSkeleton,
    Skeleton
  }
}
</script>
