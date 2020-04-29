class FormJSONMap(object):
    """Switcher class for building dict that will be post to pscheduler api as json
        Each method gets called corresponding to the name of form field

    Attributes
    ----------
    argkey : str
        submitted form field name
    argval : 
        submitted form field value
    tdict - dict
        dictionary to be converted to json
    """

    def map_form_to_json(self, argkey, argval,  tdict):
        """Check if class method exists, convert hypens to underscores
        (v_ added for security) and call method
        """
        
        mname = str(argkey)
        method_name = 'v_' + mname.replace("-", "_")
        if hasattr(self, method_name):
            # Get the method from 'self'. Default to a lambda.
            method = getattr(self, method_name,  '')
            # Call the method as we return it
            return method(argval,  tdict)
 
    # common
    def v_select_test(self,  argval,  tdict):
        tdict["test"]["type"] = argval
 
    def v_select_source(self,  argval,  tdict):
        tdict["test"]["spec"]["source"] = argval
        
    def v_select_dest(self,  argval,  tdict):
        tdict["test"]["spec"]["dest"] = argval
    
    # throughput
    def v_select_throughput_protocol(self,  argval,  tdict):
        if argval == "udp":
            tdict["test"]["spec"]["udp"] = True

    def v_throughput_test_duration_submit(self,  argval,  tdict):
        tdict["test"]["spec"]["duration"] = argval

    def v_throughput_select_tools(self,  argval,  tdict):
        if "tools" in tdict:
            tdict["tools"].append(argval)
        else:
            tdict["tools"] = [argval]

    def v_throughput_parallel_streams(self,  argval,  tdict):
        tdict["test"]["spec"]["parallel"] = int(argval)

    def v_throughput_omit_interval_submit(self,  argval,  tdict):
        if argval and argval != '0':
            tdict["test"]["spec"]["omit"] = argval

    def v_throughput_tos_bits(self,  argval,  tdict):
        if argval and argval != '0':
            tdict["test"]["spec"]["ip-tos"] = int(argval)


    #rtt
    def v_rtt_time_between_tests_submit(self,  argval,  tdict):
        tdict["test"]["spec"]["interval"] = argval

    def v_rtt_packets_per_test(self,  argval,  tdict):
        tdict["test"]["spec"]["count"] = int(argval)

    def v_rtt_time_between_packets_submit(self,  argval,  tdict):
        tdict["test"]["spec"]["timeout"] = argval

    def v_rtt_packet_size(self,  argval,  tdict):
        tdict["test"]["spec"]["length"] = int(argval)

    #latency
    def v_latency_packet_count(self,  argval,  tdict):
        tdict["test"]["spec"]["packet-count"] = int(argval)

    def v_latency_packet_interval(self,  argval,  tdict):
        tdict["test"]["spec"]["packet-interval"] = float(argval)

    def v_latency_packet_timeout(self,  argval,  tdict):
        tdict["test"]["spec"]["packet-timeout"] = int(argval)

    def v_latency_packet_padding(self,  argval,  tdict):
        tdict["test"]["spec"]["packet-padding"] = int(argval)

    #trace
    def v_trace_first_ttl(self,  argval,  tdict):
        tdict["test"]["spec"]["first-ttl"] = int(argval)

    def v_trace_max_ttl(self,  argval,  tdict):
        tdict["test"]["spec"]["hops"] = int(argval)

    def v_trace_select_tools(self,  argval,  tdict):
        if "tools" in tdict:
            tdict["tools"].append(argval)
        else:
            tdict["tools"] = [argval]
