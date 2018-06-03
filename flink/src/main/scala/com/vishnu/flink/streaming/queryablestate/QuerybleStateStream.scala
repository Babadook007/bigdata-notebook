package com.vishnu.flink.streaming.queryablestate

import org.apache.flink.api.common.functions.ReduceFunction
import org.apache.flink.api.common.state.ReducingStateDescriptor
import org.apache.flink.api.common.typeinfo.{TypeHint, TypeInformation}
import org.apache.flink.api.java.tuple.Tuple
import org.apache.flink.api.scala._
import org.apache.flink.streaming.api.scala.StreamExecutionEnvironment
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.streaming.api.windowing.windows.TimeWindow
import org.apache.flink.util.Collector
import org.apache.log4j.Logger

/**
  * Created by vviswanath on 3/12/17.
  */

object QuerybleStateStream {

  val logger = Logger.getLogger("QueryableStateStream")

  case class ClimateLog(country: String, state: String, temperature: Float, humidity: Float)
  object ClimateLog {
    def apply(line: String): Option[ClimateLog] = {
      val parts = line.split(",")
      try{
        Some(ClimateLog(parts(0), parts(1), parts(2).toFloat, parts(3).toFloat))
      } catch {
        case e: Exception => {
          logger.warn(s"Unable to parse line $line")
          None
        }
      }
    }
  }

  def main(args: Array[String]): Unit = {
    val senv = StreamExecutionEnvironment.getExecutionEnvironment
    senv.setParallelism(1)

    //this is required if org.apache.flink.api.scala._ is not imported
    //implicit val typeInfo = TypeInformation.of(classOf[ClimateLog])

    val climateLogStream = senv.socketTextStream("localhost", 2222)
      .flatMap(ClimateLog(_))

    val climateLogAgg = climateLogStream
      .name("climate-log-agg")
      .keyBy("country", "state")
      .timeWindow(Time.seconds(10))
      .reduce(reduceFunction)

    val climateLogStateDesc = new ReducingStateDescriptor[ClimateLog](
      "climate-record-state",
      reduceFunction,
      TypeInformation.of(new TypeHint[ClimateLog]() {}))


    val queryableStream = climateLogAgg
      .name("queryable-state")
      .keyBy("country")
      .asQueryableState("queryable-climatelog-stream", climateLogStateDesc)

    climateLogAgg.print()

    senv.execute("Queryablestate example streaming job")
  }

  val reduceFunction = new ReduceFunction[ClimateLog] {
    override def reduce(c1: ClimateLog, c2: ClimateLog): ClimateLog = {
      c1.copy(
        temperature = c1.temperature + c2.temperature,
        humidity=c1.humidity + c2.humidity)
    }
  }
}
